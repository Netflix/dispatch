import logging

from datetime import date

from dispatch.config import (
    INCIDENT_PLUGIN_CONVERSATION_SLUG,
    INCIDENT_PLUGIN_DOCUMENT_SLUG,
    INCIDENT_PLUGIN_STORAGE_SLUG,
    INCIDENT_RESOURCE_INCIDENT_REPORT_DOCUMENT,
    INCIDENT_STORAGE_INCIDENT_REPORT_FILE_ID,
)
from dispatch.database import SessionLocal
from dispatch.decorators import background_task
from dispatch.event import service as event_service
from dispatch.incident import service as incident_service
from dispatch.messaging import INCIDENT_STATUS_REPORT, MessageType
from dispatch.participant import service as participant_service
from dispatch.plugins.base import plugins
from dispatch.document import service as document_service
from dispatch.document.models import DocumentCreate


from .enums import ReportTypes
from .models import ReportCreate
from .service import create, get_all_by_incident_id_and_type


log = logging.getLogger(__name__)


@background_task
def create_status_report(
    user_id: str, user_email: str, incident_id: int, action: dict, db_session=None
):
    """Creates and sends a new status report to a conversation."""
    conditions = action["submission"]["conditions"]
    actions = action["submission"]["actions"]
    needs = action["submission"]["needs"]

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we create a new status report
    status_report_in = ReportCreate(
        conditions=conditions, actions=actions, needs=needs, report_type=ReportTypes.status_report
    )
    status_report = create(db_session=db_session, report_in=status_report_in)

    # we load the participant
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # we save the status report
    participant.reports.append(status_report)
    incident.reports.append(status_report)

    db_session.add(participant)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Incident Participant",
        description=f"{participant.individual.name} created a new status report",
        details={"conditions": conditions, "actions": actions, "needs": needs},
        incident_id=incident_id,
        individual_id=participant.individual.id,
    )

    # we send the status report to the conversation
    send_status_report_to_conversation(incident_id, conditions, actions, needs, db_session)

    return status_report


@background_task
def create_incident_report(
    user_id: str, user_email: str, incident_id: int, action: dict, db_session=None
):
    """Creates an incident report."""
    current_date = (date.today()).strftime("%B %d, %Y")

    current_status = action["submission"]["current_status"]
    overview = action["submission"]["overview"]
    next_steps = action["submission"]["next_steps"]

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we fetch all previous incident reports
    incident_reports = get_all_by_incident_id_and_type(
        db_session=db_session, incident_id=incident_id, report_type=ReportTypes.incident_report
    )

    previous_incident_reports = []
    for incident_report in incident_reports:
        previous_incident_reports.append(
            f"{incident_report.document.name} - {incident_report.document.weblink}\n"
        )

    # we create a new incident report
    incident_report_in = ReportCreate(
        current_status=current_status,
        overview=overview,
        next_steps=next_steps,
        report_type=ReportTypes.incident_report,
    )
    incident_report = create(db_session=db_session, report_in=incident_report_in)

    # we load the participant
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # we save the incident report
    participant.reports.append(incident_report)
    incident.reports.append(incident_report)

    db_session.add(participant)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Incident Participant",
        description=f"{participant.individual.name} created a new incident report",
        details={"current_status": current_status, "overview": overview, "next_steps": next_steps},
        incident_id=incident_id,
        individual_id=participant.individual.id,
    )

    # we create a new document for the incident report
    storage_plugin = plugins.get(INCIDENT_PLUGIN_STORAGE_SLUG)
    incident_report_document_name = f"{incident.name} - Incident Report - {current_date}"
    incident_report_document = storage_plugin.copy_file(
        team_drive_id=incident.storage.resource_id,
        file_id=INCIDENT_STORAGE_INCIDENT_REPORT_FILE_ID,
        name=incident_report_document_name,
    )

    incident_report_document.update(
        {
            "name": incident_report_document_name,
            "resource_type": INCIDENT_RESOURCE_INCIDENT_REPORT_DOCUMENT,
        }
    )

    storage_plugin.move_file(
        new_team_drive_id=incident.storage.resource_id, file_id=incident_report_document["id"]
    )

    event_service.log(
        db_session=db_session,
        source=storage_plugin.title,
        description="Incident report document added to storage",
        incident_id=incident.id,
    )

    document_in = DocumentCreate(
        name=incident_report_document["name"],
        resource_id=incident_report_document["id"],
        resource_type=incident_report_document["resource_type"],
        weblink=incident_report_document["weblink"],
    )
    incident_report.document = document_service.create(
        db_session=db_session, document_in=document_in
    )

    incident.documents.append(incident_report.document)

    db_session.add(incident_report)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident report document added to incident",
        incident_id=incident.id,
    )

    # we update the incident update document
    document_plugin = plugins.get(INCIDENT_PLUGIN_DOCUMENT_SLUG)
    document_plugin.update(
        incident_report_document["id"],
        name=incident.name,
        title=incident.title,
        current_date=current_date,
        current_status=current_status,
        overview=overview,
        next_steps=next_steps,
        previous_reports="\n".join(previous_incident_reports),
        commander_fullname=incident.commander.name,
        commander_mobile_phone=incident.commander.mobile_phone,
    )

    # we send the incident update to the distribution lists
    # send_most_recent_incident_report_to_distribution_lists(incident_id, db_session)

    return incident_report


def send_status_report_to_conversation(
    incident_id: int, conditions: str, actions: str, needs: str, db_session: SessionLocal
):
    """Sends a status report to the conversation."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send(
        incident.conversation.channel_id,
        "Incident Status Report",
        INCIDENT_STATUS_REPORT,
        notification_type=MessageType.incident_status_report,
        persist=True,
        conditions=conditions,
        actions=actions,
        needs=needs,
    )
