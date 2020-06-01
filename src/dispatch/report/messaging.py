import logging

from dispatch.config import (
    INCIDENT_PLUGIN_CONVERSATION_SLUG,
    INCIDENT_PLUGIN_EMAIL_SLUG,
    INCIDENT_RESOURCE_NOTIFICATIONS_GROUP,
)
from dispatch.conversation.enums import ConversationCommands
from dispatch.database import SessionLocal
from dispatch.group import service as group_service
from dispatch.incident import service as incident_service
from dispatch.incident.models import Incident
from dispatch.messaging import (
    INCIDENT_EXECUTIVE_REPORT,
    INCIDENT_REPORT_REMINDER,
    INCIDENT_TACTICAL_REPORT,
    MessageType,
)
from dispatch.plugins.base import plugins

from .enums import ReportTypes
from .models import Report


log = logging.getLogger(__name__)


def get_report_reminder_settings(report_type: ReportTypes):
    report_reminder_settings_map = {
        ReportTypes.tactical_report: (
            ConversationCommands.tactical_report,
            MessageType.incident_tactical_report,
        ),
        ReportTypes.executive_report: (
            ConversationCommands.tactical_report,
            MessageType.incident_executive_report,
        ),
    }

    return report_reminder_settings_map.get(report_type, (None, None))


def send_tactical_report_to_conversation(
    incident_id: int, conditions: str, actions: str, needs: str, db_session: SessionLocal
):
    """Sends a tactical report to the conversation."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send(
        incident.conversation.channel_id,
        "Incident Tactical Report",
        INCIDENT_TACTICAL_REPORT,
        notification_type=MessageType.incident_tactical_report,
        persist=True,
        conditions=conditions,
        actions=actions,
        needs=needs,
    )

    log.debug("Tactical report sent to conversation {incident.conversation.channel_id}.")


def send_executive_report_to_notifications_group(
    incident_id: int, executive_report: Report, db_session: SessionLocal,
):
    """Sends an executive report to the notifications group."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    notification_group = group_service.get_by_incident_id_and_resource_type(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_RESOURCE_NOTIFICATIONS_GROUP,
    )

    subject = f"{incident.name.upper()} - Executive Report"

    email_plugin = plugins.get(INCIDENT_PLUGIN_EMAIL_SLUG)
    email_plugin.send(
        notification_group.email,
        INCIDENT_EXECUTIVE_REPORT,
        MessageType.incident_executive_report,
        subject=subject,
        name=subject,
        title=incident.title,
        commander_fullname=incident.commander.name,
        current_status=executive_report.details.get("current_status"),
        overview=executive_report.details.get("overview"),
        next_steps=executive_report.details.get("next_steps"),
        weblink=executive_report.document.weblink,
        notifications_group=notification_group.email,
    )

    log.debug(f"Executive report sent to notifications group {notification_group.email}.")


def send_incident_report_reminder(
    incident: Incident, report_type: ReportTypes,
):
    """Sends a direct message to the incident commander indicating that they should complete a report."""
    message_text = f"Incident {report_type} Reminder"
    message_template = INCIDENT_REPORT_REMINDER
    command_name, message_type = get_report_reminder_settings(report_type)

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    report_command = convo_plugin.get_command_name(command_name)

    items = [
        {
            "command": report_command,
            "name": incident.name,
            "report_type": report_type,
            "ticket_weblink": incident.ticket.weblink,
            "title": incident.title,
        }
    ]

    convo_plugin.send_direct(
        incident.commander.email, message_text, message_template, message_type, items=items,
    )

    log.debug(f"Incident report reminder sent to {incident.commander.email}.")
