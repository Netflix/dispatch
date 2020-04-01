import logging

from dispatch.config import INCIDENT_PLUGIN_CONVERSATION_SLUG
from dispatch.database import SessionLocal
from dispatch.decorators import background_task
from dispatch.incident import service as incident_service
from dispatch.messaging import INCIDENT_STATUS_REPORT, MessageType
from dispatch.participant import service as participant_service
from dispatch.plugins.base import plugins

from .service import create, get_most_recent_by_incident_id

log = logging.getLogger(__name__)


def save_status_report(
    user_email: str,
    conditions: str,
    actions: str,
    needs: str,
    incident_id: int,
    db_session: SessionLocal,
):
    """Saves a new status report."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we create a new status report
    status_report = create(
        db_session=db_session, conditions=conditions, actions=actions, needs=needs
    )

    # we load the participant
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # we save the status report
    participant.status_reports.append(status_report)
    incident.status_reports.append(status_report)

    db_session.add(participant)
    db_session.add(incident)
    db_session.commit()

    log.debug(f"New status report created by {participant.individual.name}")


def send_most_recent_status_report_to_conversation(incident_id: int, db_session: SessionLocal):
    """Sends most recent status report to the conversation."""
    # we load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we load the most recent status report
    status_report = get_most_recent_by_incident_id(db_session=db_session, incident_id=incident_id)

    # we send the status report to the conversation
    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send(
        incident.conversation.channel_id,
        "Incident Status Report",
        INCIDENT_STATUS_REPORT,
        notification_type=MessageType.incident_status_report,
        persist=True,
        conditions=status_report.conditions,
        actions=status_report.actions,
        needs=status_report.needs,
    )

    log.debug(f"Status report sent to conversation {incident.conversation.channel_id}")


@background_task
def new_status_report_flow(
    user_id: str, user_email: str, incident_id: int, action: dict, db_session=None
):
    """Stores and sends a new status report to a conversation."""
    conditions = action["submission"]["conditions"]
    actions = action["submission"]["actions"]
    needs = action["submission"]["needs"]

    # we save the status report
    save_status_report(user_email, conditions, actions, needs, incident_id, db_session)

    # we send the status report to the conversation
    send_most_recent_status_report_to_conversation(incident_id, db_session)
