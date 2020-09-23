import json
import logging
import pytz
from typing import List

from datetime import datetime
from enum import Enum
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from dispatch.database import SessionLocal

from dispatch.decorators import background_task
from dispatch.event import service as event_service
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus, IncidentSlackViewBlockId, NewIncidentSubmission
from dispatch.incident.models import Incident
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.participant import service as participant_service
from dispatch.participant.models import Participant, ParticipantUpdate
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service

from .messaging import create_incident_reported_confirmation_message
from .service import get_user_profile_by_email


slack_client = dispatch_slack_service.create_slack_client()
log = logging.getLogger(__name__)


class UpdateParticipantBlockFields(str, Enum):
    reason_added = "reason_added_field"
    participant = "selected_participant_field"


class UpdateParticipantCallbacks(str, Enum):
    submit_form = "update_participant_submit_form"
    update_view = "update_participant_update_view"


class UpdateNotificationsGroupBlockFields(str, Enum):
    update_members = "update_members_field"


class UpdateNotificationsGroupCallbacks(str, Enum):
    submit_form = "update_notifications_group_submit_form"


class AddTimelineEventBlockFields(str, Enum):
    date = "date_field"
    hour = "hour_field"
    minute = "minute_field"
    timezone = "timezone_field"
    description = "description_field"


class AddTimelineEventCallbacks(str, Enum):
    submit_form = "add_timeline_event_submit_form"


class RunExternalWorkflowBlockFields(str, Enum):
    workflow_select = "run_external_workflow_select"
    param = "run_external_workflow_param"


class RunExternalWorkflowCallbacks(str, Enum):
    submit_form = "run_external_workflow_submit_form"
    update_view = "run_external_workflow_update_view"


def handle_modal_action(action: dict, background_tasks: BackgroundTasks):
    """Handles all modal actions."""
    view_data = action["view"]
    view_data["private_metadata"] = json.loads(view_data["private_metadata"])

    action_id = view_data["callback_id"]

    for f in action_functions(action_id):
        background_tasks.add_task(f, action)


def action_functions(action_id: str):
    """Determines which function needs to be run."""
    action_mappings = {
        AddTimelineEventCallbacks.submit_form: [add_timeline_event_from_submitted_form],
        NewIncidentSubmission.form_slack_view: [report_incident_from_submitted_form],
        UpdateParticipantCallbacks.submit_form: [update_participant_from_submitted_form],
        UpdateParticipantCallbacks.update_view: [update_update_participant_modal],
        UpdateNotificationsGroupCallbacks.submit_form: [
            update_notifications_group_from_submitted_form
        ],
        RunExternalWorkflowCallbacks.update_view: [update_external_workflow_modal],
        RunExternalWorkflowCallbacks.submit_form: [run_external_workflow_submitted_form],
    }

    # this allows for unique action blocks e.g. invite-user or invite-user-1, etc
    for key in action_mappings.keys():
        if key in action_id:
            return action_mappings[key]
    return []


def parse_submitted_form(view_data: dict):
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
            elif elem_key_value_pair.get("selected_date"):
                parsed_data[state] = elem_key_value_pair.get("selected_date")
            else:
                parsed_data[state] = elem_key_value_pair.get("value")

    return parsed_data


@background_task
def report_incident_from_submitted_form(action: dict, db_session: Session = None):
    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    requested_form_title = parsed_form_data.get(IncidentSlackViewBlockId.title)
    requested_form_description = parsed_form_data.get(IncidentSlackViewBlockId.description)
    requested_form_incident_type = parsed_form_data.get(IncidentSlackViewBlockId.type)
    requested_form_incident_priority = parsed_form_data.get(IncidentSlackViewBlockId.priority)

    # Send a confirmation to the user
    blocks = create_incident_reported_confirmation_message(
        title=requested_form_title,
        incident_type=requested_form_incident_type.get("value"),
        incident_priority=requested_form_incident_priority.get("value"),
    )

    user_id = action["user"]["id"]
    channel_id = submitted_form.get("private_metadata")["channel_id"]
    dispatch_slack_service.send_ephemeral_message(
        client=slack_client,
        conversation_id=channel_id,
        user_id=user_id,
        text="",
        blocks=blocks,
    )

    # Create the incident
    user_email = action["user"]["email"]
    incident = incident_service.create(
        db_session=db_session,
        title=requested_form_title,
        status=IncidentStatus.active,
        description=requested_form_description,
        incident_type=requested_form_incident_type,
        incident_priority=requested_form_incident_priority,
        reporter_email=user_email,
        tags=[],  # The modal does not currently support tags
    )

    incident_flows.incident_create_flow(incident_id=incident.id)


def create_block_option_from_template(text: str, value: str):
    """Helper function which generates the option block for modals / views"""
    return {"text": {"type": "plain_text", "text": str(text), "emoji": True}, "value": str(value)}


def build_report_incident_blocks(channel_id: str, db_session: Session):
    """Builds all blocks required for the reporting incident modal."""
    incident_type_options = []
    for incident_type in incident_type_service.get_all(db_session=db_session):
        incident_type_options.append(
            create_block_option_from_template(text=incident_type.name, value=incident_type.name)
        )

    incident_priority_options = []
    for incident_priority in incident_priority_service.get_all(db_session=db_session):
        incident_priority_options.append(
            create_block_option_from_template(
                text=incident_priority.name, value=incident_priority.name
            )
        )

    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Security Incident Report"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "If you suspect a security incident and require help from security, "
                        "please fill out the following to the best of your abilities.",
                    }
                ],
            },
            {
                "block_id": IncidentSlackViewBlockId.title,
                "type": "input",
                "label": {"type": "plain_text", "text": "Title"},
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "A brief explanatory title. You can change this later.",
                    },
                },
            },
            {
                "block_id": IncidentSlackViewBlockId.description,
                "type": "input",
                "label": {"type": "plain_text", "text": "Description"},
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "A summary of what you know so far. It's all right if this is incomplete.",
                    },
                    "multiline": True,
                },
            },
            {
                "block_id": IncidentSlackViewBlockId.type,
                "type": "input",
                "label": {"type": "plain_text", "text": "Type"},
                "element": {
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select Incident Type"},
                    "options": incident_type_options,
                },
            },
            {
                "block_id": IncidentSlackViewBlockId.priority,
                "type": "input",
                "label": {"type": "plain_text", "text": "Priority", "emoji": True},
                "element": {
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select Incident Priority"},
                    "options": incident_priority_options,
                },
            },
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "callback_id": NewIncidentSubmission.form_slack_view,
        "private_metadata": json.dumps({"channel_id": str(channel_id)}),
    }

    return modal_template


@background_task
def create_report_incident_modal(incident_id: int, command: dict = None, db_session=None):
    """Creates a modal for reporting an incident."""
    channel_id = command.get("channel_id")
    trigger_id = command.get("trigger_id")

    modal_create_template = build_report_incident_blocks(
        channel_id=channel_id, db_session=db_session
    )

    dispatch_slack_service.open_modal_with_user(
        client=slack_client, trigger_id=trigger_id, modal=modal_create_template
    )


def build_incident_participants_select_block(incident: Incident, participant: Participant = None):
    """Builds a static select with all current participants."""
    selected_option = None
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
    """Builds all blocks required for updating the participant modal."""
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Edit Participant"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Use this form to edit why a particpant was added to this incident.",
                    }
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

    # we need to show the reason if we're updating
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
    submitted_form = action.get("view")

    parsed_form_data = parse_submitted_form(submitted_form)

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
    """Creates a modal for updating a participant."""
    trigger_id = command["trigger_id"]

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_create_template = build_update_participant_blocks(incident=incident)

    dispatch_slack_service.open_modal_with_user(
        client=slack_client, trigger_id=trigger_id, modal=modal_create_template
    )


def build_update_notifications_group_blocks(incident: Incident, db_session: SessionLocal):
    """Builds all blocks required to update the membership of the notifications group."""
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Update Group Membership"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Use this form to update the membership of the notifications group.",
                    }
                ],
            },
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Update"},
        "callback_id": UpdateNotificationsGroupCallbacks.submit_form,
        "private_metadata": json.dumps({"incident_id": str(incident.id)}),
    }

    group_plugin = plugin_service.get_active(db_session=db_session, plugin_type="participant-group")
    members = group_plugin.instance.list(incident.notifications_group.email)

    members_block = {
        "type": "input",
        "block_id": UpdateNotificationsGroupBlockFields.update_members,
        "label": {"type": "plain_text", "text": "Members"},
        "element": {
            "type": "plain_text_input",
            "action_id": UpdateNotificationsGroupBlockFields.update_members,
            "multiline": True,
            "initial_value": (", ").join(members),
        },
    }
    modal_template["blocks"].append(members_block)

    modal_template["blocks"].append(
        {
            "type": "context",
            "elements": [{"type": "plain_text", "text": "Separate email addresses with commas."}],
        },
    )

    return modal_template


@background_task
def create_update_notifications_group_modal(incident_id: int, command: dict, db_session=None):
    """Creates a modal for editing members of the notifications group."""
    trigger_id = command["trigger_id"]

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_create_template = build_update_notifications_group_blocks(
        incident=incident, db_session=db_session
    )

    dispatch_slack_service.open_modal_with_user(
        client=slack_client, trigger_id=trigger_id, modal=modal_create_template
    )


@background_task
def update_notifications_group_from_submitted_form(action: dict, db_session=None):
    """Updates notifications group based on submitted form data."""
    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    current_members = (
        submitted_form["blocks"][1]["element"]["initial_value"].replace(" ", "").split(",")
    )
    updated_members = (
        parsed_form_data.get(UpdateNotificationsGroupBlockFields.update_members)
        .replace(" ", "")
        .split(",")
    )

    members_added = list(set(updated_members) - set(current_members))
    members_removed = list(set(current_members) - set(updated_members))

    incident_id = action["view"]["private_metadata"]["incident_id"]
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    group_plugin = plugin_service.get_active(db_session=db_session, plugin_type="participant-group")

    group_plugin.instance.add(incident.notifications_group.email, members_added)
    group_plugin.instance.remove(incident.notifications_group.email, members_removed)


def build_add_timeline_event_blocks(incident: Incident):
    """Builds all blocks required to add an event to the incident timeline."""
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Add Timeline Event"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Use this form to add an event to the incident timeline.",
                    }
                ],
            },
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Add"},
        "callback_id": AddTimelineEventCallbacks.submit_form,
        "private_metadata": json.dumps({"incident_id": str(incident.id)}),
    }

    date_picker_block = {
        "type": "input",
        "block_id": AddTimelineEventBlockFields.date,
        "label": {"type": "plain_text", "text": "Date"},
        "element": {"type": "datepicker"},
        "optional": False,
    }
    modal_template["blocks"].append(date_picker_block)

    hour_picker_options = []
    for h in range(0, 24):
        h = str(h).zfill(2)
        hour_picker_options.append(create_block_option_from_template(text=f"{h}:00", value=h))

    hour_picker_block = {
        "type": "input",
        "block_id": AddTimelineEventBlockFields.hour,
        "label": {"type": "plain_text", "text": "Hour"},
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select an hour"},
            "options": hour_picker_options,
        },
        "optional": False,
    }
    modal_template["blocks"].append(hour_picker_block)

    minute_picker_options = []
    for m in range(0, 60):
        minute_picker_options.append(
            create_block_option_from_template(text=m, value=str(m).zfill(2))
        )

    minute_picker_block = {
        "type": "input",
        "block_id": AddTimelineEventBlockFields.minute,
        "label": {"type": "plain_text", "text": "Minute"},
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select a minute"},
            "options": minute_picker_options,
        },
        "optional": False,
    }
    modal_template["blocks"].append(minute_picker_block)

    timezone_block = {
        "type": "input",
        "block_id": AddTimelineEventBlockFields.timezone,
        "label": {"type": "plain_text", "text": "Time Zone"},
        "element": {
            "type": "radio_buttons",
            "initial_option": {
                "value": "profile",
                "text": {"type": "plain_text", "text": "Local time from Slack profile"},
            },
            "options": [
                {
                    "text": {"type": "plain_text", "text": "Local time from Slack profile"},
                    "value": "profile",
                },
                {
                    "text": {"type": "plain_text", "text": "Coordinated Universal Time (UTC)"},
                    "value": "UTC",
                },
            ],
        },
    }
    modal_template["blocks"].append(timezone_block)

    description_block = {
        "type": "input",
        "block_id": AddTimelineEventBlockFields.description,
        "label": {"type": "plain_text", "text": "Description"},
        "element": {
            "type": "plain_text_input",
            "action_id": AddTimelineEventBlockFields.description,
            "placeholder": {"type": "plain_text", "text": "A description of the event"},
        },
        "optional": False,
    }
    modal_template["blocks"].append(description_block)

    return modal_template


@background_task
def create_add_timeline_event_modal(incident_id: int, command: dict, db_session=None):
    """Creates a modal for adding events to the incident timeline."""
    trigger_id = command["trigger_id"]

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_create_template = build_add_timeline_event_blocks(incident=incident)

    dispatch_slack_service.open_modal_with_user(
        client=slack_client, trigger_id=trigger_id, modal=modal_create_template
    )


@background_task
def add_timeline_event_from_submitted_form(action: dict, db_session=None):
    """Adds event to incident timeline based on submitted form data."""
    user_email = action["user"]["email"]

    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    event_date = parsed_form_data.get(AddTimelineEventBlockFields.date)
    event_hour = parsed_form_data.get(AddTimelineEventBlockFields.hour)["value"]
    event_minute = parsed_form_data.get(AddTimelineEventBlockFields.minute)["value"]
    event_timezone_selection = parsed_form_data.get(AddTimelineEventBlockFields.timezone)["value"]
    event_description = parsed_form_data.get(AddTimelineEventBlockFields.description)

    incident_id = action["view"]["private_metadata"]["incident_id"]

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    event_timezone = event_timezone_selection
    if event_timezone_selection == "profile":
        participant_profile = get_user_profile_by_email(slack_client, user_email)
        if participant_profile.get("tz"):
            event_timezone = participant_profile.get("tz")

    event_dt = datetime.fromisoformat(f"{event_date}T{event_hour}:{event_minute}")
    event_dt_utc = pytz.timezone(event_timezone).localize(event_dt).astimezone(pytz.utc)

    event_service.log(
        db_session=db_session,
        source="Slack Plugin - Conversation Management",
        started_at=event_dt_utc,
        description=f'"{event_description}," said {participant.individual.name}',
        incident_id=incident_id,
        individual_id=participant.individual.id,
    )


def build_external_workflow_blocks(
    incident: Incident, workflows: List[dict], selected_workflow: dict = None
):
    """Builds all blocks required to run an external workflow."""
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Run external workflow"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Use this form to run an external workflow.",
                    }
                ],
            },
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Run"},
        "callback_id": RunExternalWorkflowCallbacks.update_view,
        "private_metadata": json.dumps({"incident_id": str(incident.id)}),
    }

    selected_option = None
    workflow_options = []
    for w in workflows:
        current_option = {
            "text": {
                "type": "plain_text",
                "text": w["name"],
            },
            "value": w["id"],
        }

        workflow_options.append(current_option)

        if selected_workflow:
            if w["id"] == selected_workflow["id"]:
                selected_option = current_option

    if selected_workflow:
        select_block = {
            "block_id": RunExternalWorkflowBlockFields.workflow_select,
            "type": "input",
            "element": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select Workflow",
                },
                "initial_option": selected_option,
                "options": workflow_options,
                "action_id": RunExternalWorkflowBlockFields.workflow_select,
            },
            "label": {"type": "plain_text", "text": "Workflow"},
        }
    else:
        select_block = {
            "block_id": RunExternalWorkflowBlockFields.workflow_select,
            "type": "actions",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select Workflow",
                    },
                    "options": workflow_options,
                }
            ],
        }

    modal_template["blocks"].append(select_block)

    return modal_template


@background_task
def create_run_external_workflow_modal(incident_id: int, command: dict = None, db_session=None):
    """Creates a modal for running an external workflow."""
    trigger_id = command.get("trigger_id")

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    plugin = plugin_service.get_active(plugin_type="external-workflow", db_session=db_session)
    if plugin:
        modal_create_template = build_external_workflow_blocks(
            incident=incident, workflows=plugin.instance.list()
        )

        dispatch_slack_service.open_modal_with_user(
            client=slack_client, trigger_id=trigger_id, modal=modal_create_template
        )
    else:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "No external workflow plugin is enabled. You can enable one in the Dispatch UI at /plugins.",
                },
            }
        ]
        dispatch_slack_service.send_ephemeral_message(
            slack_client,
            command["channel_id"],
            command["user_id"],
            "No external workflow plugin.",
            blocks=blocks,
        )


@background_task
def update_external_workflow_modal(action: dict, db_session=None):
    """Pushes an updated view to the run workflow modal."""
    trigger_id = action["trigger_id"]
    incident_id = action["view"]["private_metadata"]["incident_id"]
    workflow_id = action["actions"][0]["selected_option"]["value"]

    plugin = plugin_service.get_active(plugin_type="external-workflow", db_session=db_session)
    selected_workflow = plugin.instance.get(workflow_id)
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_template = build_external_workflow_blocks(
        incident=incident, workflows=plugin.instance.list(), selected_workflow=selected_workflow
    )

    modal_template["blocks"].append(
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Workflow Parameters*"}}
    )

    for p in selected_workflow["params"]:
        modal_template["blocks"].append(
            {
                "block_id": f"{RunExternalWorkflowBlockFields.param}-{p['name']}",
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {"type": "plain_text", "text": "Value"},
                },
                "label": {"type": "plain_text", "text": p["name"]},
            }
        )

    modal_template["callback_id"] = RunExternalWorkflowCallbacks.submit_form

    dispatch_slack_service.update_modal_with_user(
        client=slack_client,
        trigger_id=trigger_id,
        view_id=action["view"]["id"],
        modal=modal_template,
    )


@background_task
def run_external_workflow_submitted_form(action: dict, db_session=None):
    """Runs an external flow."""
    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    params = {}
    for i in parsed_form_data.keys():
        if i.startswith(RunExternalWorkflowBlockFields.param):
            key = i.split("-")[1]
            value = parsed_form_data[i]
            params.update({key: value})

    workflow_id = parsed_form_data.get(RunExternalWorkflowBlockFields.workflow_select)["value"]
    incident_id = action["view"]["private_metadata"]["incident_id"]
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    params.update({"incident_id": incident.id, "incident_name": incident.name})
    plugin = plugin_service.get_active(plugin_type="external-workflow", db_session=db_session)

    workflow_resource = plugin.instance.run(workflow_id, params)

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Workflow has been started.",
            },
        }
    ]

    dispatch_slack_service.send_ephemeral_message(
        slack_client,
        incident.conversation.channel_id,
        command["user_id"],
        "No external workflow plugin.",
        blocks=blocks,
    )
