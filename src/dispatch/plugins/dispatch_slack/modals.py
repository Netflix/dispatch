import logging
import json
from enum import Enum

from sqlalchemy.orm import Session

from fastapi import BackgroundTasks

from dispatch.decorators import background_task
from dispatch.incident.enums import IncidentStatus, IncidentSlackViewBlockId, NewIncidentSubmission
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.incident import service as incident_service
from dispatch.incident import flows as incident_flows
from dispatch.incident.models import Incident
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.participant import service as participant_service
from dispatch.participant.models import Participant, ParticipantUpdate

from .messaging import (
    create_incident_reported_confirmation_msg,
    create_modal_content,
)

slack_client = dispatch_slack_service.create_slack_client()
log = logging.getLogger(__name__)


class UpdateParticipantBlockFields(str, Enum):
    reason_added = "reason_added_field"
    participant = "selected_participant_field"


class UpdateParticipantCallbacks(str, Enum):
    submit_form = "update_participant_submit_form"
    update_view = "update_participant_update_view"


def handle_modal_action(action: dict, background_tasks: BackgroundTasks):
    """Handels all modal actions."""
    view_data = action["view"]
    view_data["private_metadata"] = json.loads(view_data["private_metadata"])

    action_id = view_data["callback_id"]

    for f in action_functions(action_id):
        background_tasks.add_task(f, action)


def action_functions(action_id: str):
    """Determines which function needs to be run."""
    action_mappings = {
        NewIncidentSubmission.form_slack_view: [report_incident_from_submitted_form],
        UpdateParticipantCallbacks.submit_form: [update_participant_from_submitted_form],
        UpdateParticipantCallbacks.update_view: [update_update_participant_modal],
    }

    # this allows for unique action blocks e.g. invite-user or invite-user-1, etc
    for key in action_mappings.keys():
        if key in action_id:
            return action_mappings[key]
    return []


def parse_submitted_incident_report_form(view_data: dict):
    """Parse the submitted data and return important / required fields for Dispatch to create an incident."""
    parsed_data = {}
    state_elem = view_data.get("state")
    state_values = state_elem.get("values")
    for state in state_values:
        state_key_value_pair = state_values[state]

        for elem_key in state_key_value_pair:
            elem_key_value_pair = state_values[state][elem_key]

            if elem_key_value_pair.get("selected_option") and elem_key_value_pair.get(
                "selected_option"
            ).get("value"):
                parsed_data[state] = {
                    "name": elem_key_value_pair.get("selected_option").get("text").get("text"),
                    "value": elem_key_value_pair.get("selected_option").get("value"),
                }
            else:
                parsed_data[state] = elem_key_value_pair.get("value")

    return parsed_data


@background_task
def report_incident_from_submitted_form(
    user_id: str, user_email: str, incident_id: int, action: dict, db_session: Session = None,
):
    submitted_form = action.get("view")

    # Fetch channel id from private metadata field
    channel_id = submitted_form.get("private_metadata")

    parsed_form_data = parse_submitted_incident_report_form(submitted_form)

    requested_form_title = parsed_form_data.get(IncidentSlackViewBlockId.title)
    requested_form_description = parsed_form_data.get(IncidentSlackViewBlockId.description)
    requested_form_incident_type = parsed_form_data.get(IncidentSlackViewBlockId.type)
    requested_form_incident_priority = parsed_form_data.get(IncidentSlackViewBlockId.priority)

    # send a confirmation to the user
    msg_template = create_incident_reported_confirmation_msg(
        title=requested_form_title,
        incident_type=requested_form_incident_type.get("value"),
        incident_priority=requested_form_incident_priority.get("value"),
    )

    dispatch_slack_service.send_ephemeral_message(
        client=slack_client,
        conversation_id=channel_id,
        user_id=user_id,
        text="",
        blocks=msg_template,
    )

    # create the incident
    incident = incident_service.create(
        db_session=db_session,
        title=requested_form_title,
        status=IncidentStatus.active,
        description=requested_form_description,
        incident_type=requested_form_incident_type,
        incident_priority=requested_form_incident_priority,
        reporter_email=user_email,
    )

    incident_flows.incident_create_flow(incident_id=incident.id)


@background_task
def create_report_incident_modal(command: dict = None, db_session=None):
    """
    Prepare the Modal / View x
    Ask slack to open a modal with the prepared Modal / View content
    """
    channel_id = command.get("channel_id")
    trigger_id = command.get("trigger_id")

    type_options = []
    for t in incident_type_service.get_all(db_session=db_session):
        type_options.append({"label": t.name, "value": t.name})

    priority_options = []
    for priority in incident_priority_service.get_all(db_session=db_session):
        priority_options.append({"label": priority.name, "value": priority.name})

    modal_view_template = create_modal_content(
        channel_id=channel_id, incident_types=type_options, incident_priorities=priority_options
    )

    dispatch_slack_service.open_modal_with_user(
        client=slack_client, trigger_id=trigger_id, modal=modal_view_template
    )


def build_incident_participants_select_block(incident: Incident, participant: Participant = None):
    """Builds a static select with all current participants."""
    participant_options = []
    for p in incident.participants:
        current_option = {
            "text": {"type": "plain_text", "text": p.individual.name},
            "value": str(p.id),
        }

        participant_options.append(current_option)

        if participant:
            if p.id == participant.id:
                selected_option = current_option

    if participant:
        select_block = {
            "block_id": UpdateParticipantBlockFields.participant,
            "type": "input",
            "element": {
                "type": "static_select",
                "placeholder": {"type": "plain_text", "text": "Select Participant"},
                "options": participant_options,
                "initial_option": selected_option,
                "action_id": UpdateParticipantBlockFields.participant,
            },
            "label": {"type": "plain_text", "text": "Participant"},
        }

    else:
        select_block = {
            "block_id": UpdateParticipantBlockFields.participant,
            "type": "actions",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select Participant"},
                    "options": participant_options,
                }
            ],
        }

    return select_block


def build_update_participant_blocks(incident: Incident, participant: Participant = None):
    """Builds all blocks required for update participant modal."""
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Edit Participant"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "Edit why a particpant was added to this incident."}
                ],
            },
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "callback_id": UpdateParticipantCallbacks.update_view,
        "private_metadata": json.dumps({"incident_id": str(incident.id)}),
    }

    select_block = build_incident_participants_select_block(
        incident=incident, participant=participant
    )
    modal_template["blocks"].append(select_block)

    # we need to show the reason if we're updateing
    if participant:
        modal_template["blocks"].append(
            {
                "block_id": UpdateParticipantBlockFields.reason_added,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "initial_value": participant.added_reason or "",
                    "action_id": UpdateParticipantBlockFields.reason_added,
                },
                "label": {"type": "plain_text", "text": "Reason Added"},
            }
        )

        modal_template["callback_id"] = UpdateParticipantCallbacks.submit_form

    return modal_template


@background_task
def update_participant_from_submitted_form(action: dict, db_session=None):
    """Saves form data."""
    # Fetch channel id from private metadata field
    submitted_form = action.get("view")

    parsed_form_data = parse_submitted_incident_report_form(submitted_form)

    added_reason = parsed_form_data.get(UpdateParticipantBlockFields.reason_added)
    participant_id = int(parsed_form_data.get(UpdateParticipantBlockFields.participant)["value"])
    selected_participant = participant_service.get(
        db_session=db_session, participant_id=participant_id
    )
    participant_service.update(
        db_session=db_session,
        participant=selected_participant,
        participant_in=ParticipantUpdate(added_reason=added_reason),
    )


@background_task
def update_update_participant_modal(action: dict, db_session=None):
    """Pushes an updated view to the update participant modal."""
    trigger_id = action["trigger_id"]
    incident_id = action["view"]["private_metadata"]["incident_id"]

    participant_id = action["actions"][0]["selected_option"]["value"]

    selected_participant = participant_service.get(
        db_session=db_session, participant_id=participant_id
    )
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_update_template = build_update_participant_blocks(
        incident=incident, participant=selected_participant
    )

    dispatch_slack_service.update_modal_with_user(
        client=slack_client,
        trigger_id=trigger_id,
        view_id=action["view"]["id"],
        modal=modal_update_template,
    )


@background_task
def create_update_participant_modal(incident_id: int, command: dict, db_session=None):
    """Creates a modal for updateing a participant."""
    trigger_id = command["trigger_id"]

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_create_template = build_update_participant_blocks(incident=incident)

    dispatch_slack_service.open_modal_with_user(
        client=slack_client, trigger_id=trigger_id, modal=modal_create_template
    )
