import json

from dispatch.database.core import SessionLocal
from dispatch.incident import service as incident_service
from dispatch.incident.models import Incident
from dispatch.participant.models import Participant
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service

from .enums import (
    AddTimelineEventBlockId,
    AddTimelineEventCallbackId,
    ReportIncidentCallbackId,
    UpdateIncidentCallbackId,
    UpdateNotificationsGroupBlockId,
    UpdateNotificationsGroupCallbackId,
    UpdateParticipantBlockId,
    UpdateParticipantCallbackId,
)

from .fields import (
    description_input_block,
    incident_priority_select_block,
    incident_severity_select_block,
    incident_type_select_block,
    option_from_template,
    participants_select_block,
    project_select_block,
    resolution_input_block,
    status_select_block,
    tag_multi_select_block,
    title_input_block,
)


def update_incident(db_session: SessionLocal, channel_id: str, incident_id: int = None):
    """Builds all blocks required for the update incident modal."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Update Incident"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Use this form to update the incident details.",
                    }
                ],
            },
            title_input_block(initial_value=incident.title),
            description_input_block(initial_value=incident.description),
            resolution_input_block(initial_value=incident.resolution),
            status_select_block(initial_option=incident.status),
            incident_type_select_block(
                db_session=db_session,
                initial_option=incident.incident_type,
                project_id=incident.project.id,
            ),
            incident_severity_select_block(
                db_session=db_session,
                initial_option=incident.incident_severity,
                project_id=incident.project.id,
            ),
            incident_priority_select_block(
                db_session=db_session,
                initial_option=incident.incident_priority,
                project_id=incident.project.id,
            ),
            tag_multi_select_block(initial_options=incident.tags),
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "callback_id": UpdateIncidentCallbackId.submit_form,
        "private_metadata": json.dumps({"channel_id": str(channel_id), "incident_id": incident.id}),
    }

    return modal_template


def report_incident(
    db_session: SessionLocal,
    channel_id: str,
    project_name: str = None,
    title: str = None,
    description: str = None,
):
    """Builds all blocks required for the reporting incident modal."""
    project = project_service.get_by_name(db_session=db_session, name=project_name)
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Incident Report"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "If you suspect an incident and need help, "
                        "please fill out this form to the best of your abilities.",
                    }
                ],
            },
            title_input_block(initial_value=title),
            description_input_block(initial_value=description),
            project_select_block(db_session=db_session, initial_option=project),
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "callback_id": ReportIncidentCallbackId.update_view,
        "private_metadata": json.dumps({"channel_id": str(channel_id)}),
    }

    # switch from update to submit when we have a project
    if project:
        modal_template["callback_id"] = ReportIncidentCallbackId.submit_form
        modal_template["blocks"] += [
            incident_type_select_block(db_session=db_session, project_id=project.id),
            incident_priority_select_block(db_session=db_session, project_id=project.id),
            tag_multi_select_block(),
        ]

    return modal_template


def update_participant(incident: Incident, participant: Participant = None):
    """Builds all blocks required for updating the participant modal."""
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Update Participant"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Use this form to update the reason why the participant was added to the incident.",
                    }
                ],
            },
            participants_select_block(incident=incident, initial_option=participant),
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "callback_id": UpdateParticipantCallbackId.update_view,
        "private_metadata": json.dumps(
            {"incident_id": str(incident.id), "channel_id": str(incident.conversation.channel_id)}
        ),
    }

    # we need to show the reason if we're updating
    if participant:
        modal_template["blocks"].append(
            {
                "block_id": UpdateParticipantBlockId.reason_added,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "multiline": True,
                    "initial_value": participant.added_reason or "",
                    "action_id": UpdateParticipantBlockId.reason_added,
                },
                "label": {"type": "plain_text", "text": "Reason Added"},
            }
        )

        modal_template["callback_id"] = UpdateParticipantCallbackId.submit_form

    return modal_template


def update_notifications_group(incident: Incident, db_session: SessionLocal):
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
        "submit": {"type": "plain_text", "text": "Submit"},
        "callback_id": UpdateNotificationsGroupCallbackId.submit_form,
        "private_metadata": json.dumps(
            {"incident_id": str(incident.id), "channel_id": incident.conversation.channel_id}
        ),
    }

    group_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )
    members = group_plugin.instance.list(incident.notifications_group.email)

    members_block = {
        "type": "input",
        "block_id": UpdateNotificationsGroupBlockId.update_members,
        "label": {"type": "plain_text", "text": "Members"},
        "element": {
            "type": "plain_text_input",
            "action_id": UpdateNotificationsGroupBlockId.update_members,
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


def add_timeline_event(incident: Incident):
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
        "submit": {"type": "plain_text", "text": "Submit"},
        "callback_id": AddTimelineEventCallbackId.submit_form,
        "private_metadata": json.dumps(
            {"incident_id": str(incident.id), "channel_id": str(incident.conversation.channel_id)}
        ),
    }

    date_picker_block = {
        "type": "input",
        "block_id": AddTimelineEventBlockId.date,
        "label": {"type": "plain_text", "text": "Date"},
        "element": {"type": "datepicker"},
        "optional": False,
    }
    modal_template["blocks"].append(date_picker_block)

    hour_picker_options = []
    for h in range(0, 24):
        h = str(h).zfill(2)
        hour_picker_options.append(option_from_template(text=f"{h}:00", value=h))

    hour_picker_block = {
        "type": "input",
        "block_id": AddTimelineEventBlockId.hour,
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
        minute_picker_options.append(option_from_template(text=m, value=str(m).zfill(2)))

    minute_picker_block = {
        "type": "input",
        "block_id": AddTimelineEventBlockId.minute,
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
        "block_id": AddTimelineEventBlockId.timezone,
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
        "block_id": AddTimelineEventBlockId.description,
        "label": {"type": "plain_text", "text": "Description"},
        "element": {
            "type": "plain_text_input",
            "action_id": AddTimelineEventBlockId.description,
            "placeholder": {"type": "plain_text", "text": "A description of the event"},
        },
        "optional": False,
    }
    modal_template["blocks"].append(description_block)

    return modal_template
