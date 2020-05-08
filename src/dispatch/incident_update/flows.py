import logging

from datetime import date

from dispatch.config import (
    INCIDENT_PLUGIN_CONVERSATION_SLUG,
    INCIDENT_PLUGIN_DOCUMENT_SLUG,
    INCIDENT_PLUGIN_STORAGE_SLUG,
    INCIDENT_RESOURCE_INCIDENT_UPDATE_DOCUMENT,
    INCIDENT_STORAGE_INCIDENT_UPDATE_FILE_ID,
)

# from dispatch.messaging import INCIDENT_UPDATE, MessageType
from dispatch.database import SessionLocal
from dispatch.decorators import background_task
from dispatch.document import service as document_service
from dispatch.document.models import DocumentCreate
from dispatch.event import service as event_service
from dispatch.incident import service as incident_service
from dispatch.participant import service as participant_service
from dispatch.plugins.base import plugins

from .models import IncidentUpdateCreate
from .service import create, get_most_recent_by_incident_id, get_by_incident_id

log = logging.getLogger(__name__)


def create_incident_update(
    user_email: str,
    current_status: str,
    overview: str,
    next_steps: str,
    incident_id: int,
    db_session: SessionLocal,
):
    """Saves a new incident update."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we create a new incident update
    incident_update_in = IncidentUpdateCreate(
        current_status=current_status, overview=overview, next_steps=next_steps
    )

    incident_update = create(db_session=db_session, incident_update_in=incident_update_in)

    # we load the participant
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # we save the status report
    participant.status_reports.append(incident_update)
    incident.status_reports.append(incident_update)

    db_session.add(participant)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Incident Participant",
        description=f"{participant.individual.name} created a new incident update",
        details={"current_status": current_status, "overview": overview, "next_steps": next_steps},
        incident_id=incident_id,
        individual_id=participant.individual.id,
    )

    return incident_update


# def send_most_recent_incident_update_to_conversation(incident_id: int, db_session: SessionLocal):
#     """Sends most recent incident update to the incident conversation."""
#     # we load the incident
#     incident = incident_service.get(db_session=db_session, incident_id=incident_id)
#
#     # we load the most recent incident update
#     incident_update = get_most_recent_by_incident_id(db_session=db_session, incident_id=incident_id)
#
#     # we send the incident update to the conversation
#     convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
#     convo_plugin.send(
#         incident.conversation.channel_id,
#         "Incident Update",
#         INCIDENT_UPDATE,
#         notification_type=MessageType.incident_update,
#         persist=True,
#         overview=incident_update.overview,
#         current_status=incident_update.current_status,
#         next_steps=incident_update.next_steps,
#     )


@background_task
def new_incident_update(
    user_id: str, user_email: str, incident_id: int, action: dict, db_session=None
):
    """Stores and sends a new incident update via email."""
    current_date = (date.today()).strftime("%B %d, %Y")

    current_status = action["submission"]["current_status"]
    overview = action["submission"]["overview"]
    next_steps = action["submission"]["next_steps"]

    # we fetch all previous incident updates
    incident_updates = get_by_incident_id(db_session=db_session, incident_id=incident_id)

    previous_incident_updates = []
    for incident_update in incident_updates:
        previous_incident_updates.append(
            f"{incident_update.document.name} ({incident_update.document.weblink})"
        )

    # we create the incident update
    incident_update = create_incident_update(
        user_email, current_status, overview, next_steps, incident_id, db_session
    )

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we create a new document for the incident update
    storage_plugin = plugins.get(INCIDENT_PLUGIN_STORAGE_SLUG)
    incident_update_document_name = f"{incident.name} - Incident Update - {current_date}"
    incident_update_document = storage_plugin.copy_file(
        team_drive_id=incident.storage.resource_id,
        file_id=INCIDENT_STORAGE_INCIDENT_UPDATE_FILE_ID,
        name=incident_update_document_name,
    )

    incident_update_document.update(
        {
            "name": incident_update_document_name,
            "resource_type": INCIDENT_RESOURCE_INCIDENT_UPDATE_DOCUMENT,
        }
    )

    storage_plugin.move_file(
        new_team_drive_id=incident.storage.resource_id, file_id=incident_update_document["id"]
    )

    event_service.log(
        db_session=db_session,
        source=storage_plugin.title,
        description="Incident update document added to storage",
        incident_id=incident.id,
    )

    document_in = DocumentCreate(
        name=incident_update_document["name"],
        resource_id=incident_update_document["id"],
        resource_type=incident_update_document["resource_type"],
        weblink=incident_update_document["weblink"],
    )
    incident_update_document = document_service.create(
        db_session=db_session, document_in=document_in
    )

    incident_update.document.append(incident_update_document)
    incident.documents.append(incident_update_document)

    db_session.add(incident_update)
    db_session.add(incident)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident update document added to incident",
        incident_id=incident.id,
    )

    # we update the incident update document
    document_plugin = plugins.get(INCIDENT_PLUGIN_DOCUMENT_SLUG)
    document_plugin.update(
        incident_update_document["id"],
        name=incident.name,
        title=incident.title,
        current_date=current_date,
        current_status=current_status,
        overview=overview,
        next_steps=next_steps,
        previous_updates="\n".join(previous_incident_updates),
        commander_fullname=incident.commander.name,
        commander_mobile_phone=incident.commander.mobile_phone,
    )

    # we send the incident update to the distribution lists
    # send_most_recent_incident_update_to_distribution_lists(incident_id, db_session)

    # we send a notification about the incident review document to the conversation
    # send_incident_update_document_notification(
    #     incident.conversation.channel_id, incident_update_document["weblink"]
    # )

    # we send the incident update to the conversation
    # send_most_recent_incident_update_to_conversation(incident_id, db_session)
