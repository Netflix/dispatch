"""
.. module: dispatch.incident.flows
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""
import logging

from datetime import datetime
from typing import Any, List, Optional

from dispatch.config import (
    INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT_ID,
    INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID,
    INCIDENT_FAQ_DOCUMENT_ID,
    INCIDENT_PLUGIN_CONTACT_SLUG,
    INCIDENT_PLUGIN_CONVERSATION_SLUG,
    INCIDENT_PLUGIN_CONFERENCE_SLUG,
    INCIDENT_PLUGIN_DOCUMENT_RESOLVER_SLUG,
    INCIDENT_PLUGIN_DOCUMENT_SLUG,
    INCIDENT_PLUGIN_GROUP_SLUG,
    INCIDENT_PLUGIN_PARTICIPANT_RESOLVER_SLUG,
    INCIDENT_PLUGIN_STORAGE_SLUG,
    INCIDENT_RESOURCE_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT,
    INCIDENT_RESOURCE_FAQ_DOCUMENT,
    INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_SHEET,
    INCIDENT_RESOURCE_NOTIFICATIONS_GROUP,
    INCIDENT_RESOURCE_TACTICAL_GROUP,
    INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID,
    INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID,
    INCIDENT_STORAGE_RESTRICTED,
)

from dispatch.conference import service as conference_service
from dispatch.conference.models import ConferenceCreate
from dispatch.conversation import service as conversation_service
from dispatch.conversation.models import ConversationCreate
from dispatch.database import SessionLocal
from dispatch.decorators import background_task
from dispatch.document import service as document_service
from dispatch.document.models import DocumentCreate
from dispatch.document.service import get_by_incident_id_and_resource_type as get_document
from dispatch.enums import Visibility
from dispatch.event import service as event_service
from dispatch.group import service as group_service
from dispatch.group.models import GroupCreate
from dispatch.incident import service as incident_service
from dispatch.incident.models import IncidentRead
from dispatch.incident_priority.models import IncidentPriorityRead
from dispatch.incident_type.models import IncidentTypeRead
from dispatch.incident_type import service as incident_type_service
from dispatch.individual import service as individual_service
from dispatch.participant import flows as participant_flows
from dispatch.participant import service as participant_service
from dispatch.participant_role import flows as participant_role_flows
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.base import plugins
from dispatch.plugin import service as plugin_service
from dispatch.service import service as service_service
from dispatch.storage import service as storage_service
from dispatch.ticket import service as ticket_service
from dispatch.ticket.models import TicketCreate

from .messaging import (
    send_incident_update_notifications,
    send_incident_commander_readded_notification,
    send_incident_new_role_assigned_notification,
    send_incident_notifications,
    send_incident_participant_announcement_message,
    send_incident_participant_has_role_ephemeral_message,
    send_incident_participant_role_not_assigned_ephemeral_message,
    send_incident_resources_ephemeral_message_to_participant,
    send_incident_review_document_notification,
    send_incident_welcome_participant_messages,
    send_incident_status_report_reminder,
)
from .models import Incident, IncidentStatus

log = logging.getLogger(__name__)


def get_incident_participants(incident: Incident, db_session: SessionLocal):
    """Get additional incident participants based on priority, type, and description."""
    p = plugins.get(INCIDENT_PLUGIN_PARTICIPANT_RESOLVER_SLUG)
    individual_contacts, team_contacts = p.get(
        incident.incident_type,
        incident.incident_priority,
        incident.description,
        db_session=db_session,
    )

    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Incident participants resolved",
        incident_id=incident.id,
    )

    return individual_contacts, team_contacts


def get_incident_documents(
    db_session, incident_type: IncidentTypeRead, priority: IncidentPriorityRead, description: str
):
    """Get additional incident documents based on priority, type, and description."""
    p = plugins.get(INCIDENT_PLUGIN_DOCUMENT_RESOLVER_SLUG)
    documents = p.get(incident_type, priority, description, db_session=db_session)
    return documents


def create_incident_ticket(incident: Incident, incident_type_plugin_metadata: dict,
                           db_session: SessionLocal):
    """Create an external ticket for tracking."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="ticket")

    title = incident.title
    if incident.visibility == Visibility.restricted:
        title = incident.incident_type.name

    ticket = plugin.instance.create(
        incident.id,
        title,
        incident.incident_type.name,
        incident.incident_priority.name,
        incident.commander.email,
        incident.reporter.email,
        incident_type_plugin_metadata.get(plugin.slug)
    )
    ticket.update({"resource_type": plugin.slug})

    event_service.log(
        db_session=db_session,
        source=plugin.title,
        description="External ticket created",
        incident_id=incident.id,
    )

    return ticket


def update_incident_ticket(
    db_session: SessionLocal,
    ticket_id: str,
    title: str = None,
    description: str = None,
    incident_type: str = None,
    priority: str = None,
    status: str = None,
    commander_email: str = None,
    reporter_email: str = None,
    conversation_weblink: str = None,
    document_weblink: str = None,
    storage_weblink: str = None,
    conference_weblink: str = None,
    labels: List[str] = None,
    cost: int = None,
    visibility: str = None,
    incident_type_plugin_metadata: dict = {}
):
    """Update external incident ticket."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="ticket")

    if visibility == Visibility.restricted:
        title = description = incident_type

    plugin.instance.update(
        ticket_id,
        title=title,
        description=description,
        incident_type=incident_type,
        priority=priority,
        status=status,
        commander_email=commander_email,
        reporter_email=reporter_email,
        conversation_weblink=conversation_weblink,
        document_weblink=document_weblink,
        storage_weblink=storage_weblink,
        conference_weblink=conference_weblink,
        labels=labels,
        cost=cost,
        incident_type_plugin_metadata=incident_type_plugin_metadata.get(plugin.slug),
    )

    log.debug("The external ticket has been updated.")


def create_participant_groups(
    incident: Incident,
    direct_participants: List[Any],
    indirect_participants: List[Any],
    db_session: SessionLocal,
):
    """Create external participant groups."""
    p = plugins.get(INCIDENT_PLUGIN_GROUP_SLUG)

    group_name = f"{incident.name}"
    notification_group_name = f"{group_name}-notifications"

    direct_participant_emails = [x.email for x in direct_participants]
    tactical_group = p.create(
        group_name, direct_participant_emails
    )  # add participants to core group

    indirect_participant_emails = [x.email for x in indirect_participants]
    indirect_participant_emails.append(
        tactical_group["email"]
    )  # add all those already in the tactical group
    notification_group = p.create(notification_group_name, indirect_participant_emails)

    tactical_group.update(
        {"resource_type": INCIDENT_RESOURCE_TACTICAL_GROUP, "resource_id": tactical_group["id"]}
    )
    notification_group.update(
        {
            "resource_type": INCIDENT_RESOURCE_NOTIFICATIONS_GROUP,
            "resource_id": notification_group["id"],
        }
    )

    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Tactical and notification groups created",
        incident_id=incident.id,
    )

    return tactical_group, notification_group


def delete_participant_groups(incident: Incident, db_session: SessionLocal):
    """Deletes the external participant groups."""
    # we get the tactical group
    tactical_group = group_service.get_by_incident_id_and_resource_type(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_RESOURCE_TACTICAL_GROUP,
    )

    # we get the notifications group
    notifications_group = group_service.get_by_incident_id_and_resource_type(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_RESOURCE_NOTIFICATIONS_GROUP,
    )

    p = plugins.get(INCIDENT_PLUGIN_GROUP_SLUG)
    p.delete(email=tactical_group.email)
    p.delete(email=notifications_group.email)

    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Tactical and notification groups deleted",
        incident_id=incident.id,
    )


def create_conference(incident: Incident, participants: List[str], db_session: SessionLocal):
    """Create external conference room."""
    p = plugins.get(INCIDENT_PLUGIN_CONFERENCE_SLUG)
    conference = p.create(incident.name, participants=participants)

    conference.update(
        {"resource_type": INCIDENT_PLUGIN_CONFERENCE_SLUG, "resource_id": conference["id"]}
    )

    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Incident conference created",
        incident_id=incident.id,
    )

    return conference


def delete_conference(incident: Incident, db_session: SessionLocal):
    """Deletes the conference."""
    conference = conference_service.get_by_incident_id(
        db_session=db_session, incident_id=incident.id
    )
    p = plugins.get(INCIDENT_PLUGIN_CONFERENCE_SLUG)
    p.delete(conference.conference_id)

    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Incident conference deleted",
        incident_id=incident.id,
    )


def create_incident_storage(
    incident: Incident, participant_group_emails: List[str], db_session: SessionLocal
):
    """Create an external file store for incident storage."""
    p = plugins.get(INCIDENT_PLUGIN_STORAGE_SLUG)
    storage = p.create(incident.name, participant_group_emails)
    storage.update({"resource_type": INCIDENT_PLUGIN_STORAGE_SLUG, "resource_id": storage["id"]})

    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Incident storage created",
        incident_id=incident.id,
    )

    if INCIDENT_STORAGE_RESTRICTED:
        p.restrict(storage["resource_id"])
        event_service.log(
            db_session=db_session,
            source=p.title,
            description="Incident storage restricted",
            incident_id=incident.id,
        )

    return storage


def archive_incident_artifacts(incident: Incident, db_session: SessionLocal):
    """Archives artifacts in the incident storage."""
    p = plugins.get(INCIDENT_PLUGIN_STORAGE_SLUG)
    p.archive(
        source_team_drive_id=incident.storage.resource_id,
        dest_team_drive_id=INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID,
        folder_name=incident.name,
    )
    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Incident artifacts archived",
        incident_id=incident.id,
    )


def create_collaboration_documents(incident: Incident, db_session: SessionLocal):
    """Create external collaboration document."""
    p = plugins.get(INCIDENT_PLUGIN_STORAGE_SLUG)

    document_name = f"{incident.name} - Incident Document"

    # TODO can we make move and copy in one api call? (kglisson)
    document = p.copy_file(
        incident.storage.resource_id,
        incident.incident_type.template_document.resource_id,
        document_name,
    )
    p.move_file(incident.storage.resource_id, document["id"])

    # NOTE this should be optional
    if INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID:
        sheet_name = f"{incident.name} - Incident Tracking Sheet"
        sheet = p.copy_file(
            incident.storage.resource_id, INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID, sheet_name
        )
        p.move_file(incident.storage.resource_id, sheet["id"])

    p.create_file(incident.storage.resource_id, "logs")
    p.create_file(incident.storage.resource_id, "screengrabs")

    # TODO this logic should probably be pushed down into the plugins i.e. making them return
    # the fields we expect instead of re-mapping. (kglisson)
    document.update(
        {
            "name": document_name,
            "resource_type": INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
            "resource_id": document["id"],
        }
    )
    sheet.update(
        {
            "name": sheet_name,
            "resource_type": INCIDENT_RESOURCE_INVESTIGATION_SHEET,
            "resource_id": sheet["id"],
        }
    )

    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Incident investigation document and sheet created",
        incident_id=incident.id,
    )

    return document, sheet


def create_conversation(incident: Incident, participants: List[str], db_session: SessionLocal):
    """Create external communication conversation."""
    # we create the conversation
    p = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    conversation = p.create(incident.name, participants)

    conversation.update(
        {"resource_type": INCIDENT_PLUGIN_CONVERSATION_SLUG, "resource_id": conversation["name"]}
    )

    event_service.log(
        db_session=db_session,
        source=p.title,
        description="Incident conversation created",
        incident_id=incident.id,
    )

    return conversation


def set_conversation_topic(incident: Incident):
    """Sets the conversation topic."""
    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    conversation_topic = f":helmet_with_white_cross: {incident.commander.name} - Type: {incident.incident_type.name} - Priority: {incident.incident_priority.name} - Status: {incident.status}"
    convo_plugin.set_topic(incident.conversation.channel_id, conversation_topic)


def update_document(
    document_id: str,
    name: str,
    priority: str,
    status: str,
    type: str,
    title: str,
    description: str,
    commander_fullname: str,
    conversation_weblink: str,
    document_weblink: str,
    storage_weblink: str,
    ticket_weblink: str,
    conference_weblink: str = None,
    conference_challenge: str = None,
):
    """Update external collaboration document."""
    p = plugins.get(INCIDENT_PLUGIN_DOCUMENT_SLUG)
    p.update(
        document_id,
        name=name,
        priority=priority,
        status=status,
        type=type,
        title=title,
        description=description,
        commander_fullname=commander_fullname,
        conversation_weblink=conversation_weblink,
        document_weblink=document_weblink,
        storage_weblink=storage_weblink,
        ticket_weblink=ticket_weblink,
        conference_weblink=conference_weblink,
        conference_challenge=conference_challenge,
    )


def add_participant_to_conversation(
    participant_email: str, incident_id: int, db_session: SessionLocal
):
    """Adds a participant to the conversation."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.add(incident.conversation.channel_id, [participant_email])


@background_task
def add_participant_to_tactical_group(user_email: str, incident_id: int, db_session=None):
    """Adds participant to the tactical group."""
    # we get the tactical group
    tactical_group = group_service.get_by_incident_id_and_resource_type(
        db_session=db_session,
        incident_id=incident_id,
        resource_type=INCIDENT_RESOURCE_TACTICAL_GROUP,
    )

    p = plugins.get(INCIDENT_PLUGIN_GROUP_SLUG)
    p.add(tactical_group.email, [user_email])


# TODO create some ability to checkpoint
# We could use the model itself as the checkpoint, commiting resources as we go
# Then checking for the existence of those resources before creating them for
# this incident.
@background_task
def incident_create_flow(*, incident_id: int, checkpoint: str = None, db_session=None):
    """Creates all resources required for new incidents."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # get the incident participants based on incident type and priority
    individual_participants, team_participants = get_incident_participants(incident, db_session)

    # add individuals to incident
    for individual in individual_participants:
        participant_flows.add_participant(
            user_email=individual.email, incident_id=incident.id, db_session=db_session
        )

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident participants added to incident",
        incident_id=incident.id,
    )

    # create the incident ticket
    incident_type_data = incident_type_service.get_by_name(
        db_session=db_session, name=incident.incident_type.name
    )
    if not incident_type_data.plugin_metadata:
        incident_type_data.plugin_metadata = {}

    ticket = create_incident_ticket(incident, incident_type_data.plugin_metadata, db_session)
    incident.ticket = ticket_service.create(db_session=db_session, ticket_in=TicketCreate(**ticket))

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="External ticket added to incident",
        incident_id=incident.id,
    )

    # we set the incident name
    name = ticket["resource_id"]
    incident.name = name

    # we create the participant groups (tactical and notification)
    individual_participants = [x.individual for x in incident.participants]
    tactical_group, notification_group = create_participant_groups(
        incident, individual_participants, team_participants, db_session
    )

    for g in [tactical_group, notification_group]:
        group_in = GroupCreate(
            name=g["name"],
            email=g["email"],
            resource_type=g["resource_type"],
            resource_id=g["resource_id"],
            weblink=g["weblink"],
        )
        incident.groups.append(group_service.create(db_session=db_session, group_in=group_in))

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Tactical and notification groups added to incident",
        incident_id=incident.id,
    )

    # we create storage resource
    storage = create_incident_storage(
        incident, [tactical_group["email"], notification_group["email"]], db_session
    )
    incident.storage = storage_service.create(
        db_session=db_session,
        resource_id=storage["resource_id"],
        resource_type=storage["resource_type"],
        weblink=storage["weblink"],
    )

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Storage added to incident",
        incident_id=incident.id,
    )

    # we create the incident documents
    incident_document, incident_sheet = create_collaboration_documents(incident, db_session)

    # TODO: we need to delineate between the investigation document and suggested documents
    # # get any additional documentation based on priority or terms
    # incident_documents = get_incident_documents(
    #     db_session, incident.incident_type, incident.incident_priority, incident.description
    # )
    #
    # incident.documents = incident_documents

    faq_document = {
        "name": "Incident FAQ",
        "resource_id": INCIDENT_FAQ_DOCUMENT_ID,
        "weblink": f"https://docs.google.com/document/d/{INCIDENT_FAQ_DOCUMENT_ID}",
        "resource_type": INCIDENT_RESOURCE_FAQ_DOCUMENT,
    }

    conversation_commands_reference_document = {
        "name": "Incident Conversation Commands Reference Document",
        "resource_id": INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT_ID,
        "weblink": f"https://docs.google.com/document/d/{INCIDENT_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT_ID}",
        "resource_type": INCIDENT_RESOURCE_CONVERSATION_COMMANDS_REFERENCE_DOCUMENT,
    }

    for d in [
        incident_document,
        incident_sheet,
        faq_document,
        conversation_commands_reference_document,
    ]:
        document_in = DocumentCreate(
            name=d["name"],
            resource_id=d["resource_id"],
            resource_type=d["resource_type"],
            weblink=d["weblink"],
        )
        incident.documents.append(
            document_service.create(db_session=db_session, document_in=document_in)
        )

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Documents added to incident",
        incident_id=incident.id,
    )

    conference = create_conference(incident, [tactical_group["email"]], db_session)

    conference_in = ConferenceCreate(
        resource_id=conference["resource_id"],
        resource_type=conference["resource_type"],
        weblink=conference["weblink"],
        conference_id=conference["id"],
        conference_challenge=conference["challenge"],
    )
    incident.conference = conference_service.create(
        db_session=db_session, conference_in=conference_in
    )

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Conference added to incident",
        incident_id=incident.id,
    )

    # we create the conversation for real-time communications
    participant_emails = [x.individual.email for x in incident.participants]
    conversation = create_conversation(incident, participant_emails, db_session)

    conversation_in = ConversationCreate(
        resource_id=conversation["resource_id"],
        resource_type=conversation["resource_type"],
        weblink=conversation["weblink"],
        channel_id=conversation["id"],
    )
    incident.conversation = conversation_service.create(
        db_session=db_session, conversation_in=conversation_in
    )

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Conversation added to incident",
        incident_id=incident.id,
    )

    db_session.add(incident)
    db_session.commit()

    # we set the conversation topic
    set_conversation_topic(incident)

    # we update the incident ticket
    incident_type_data = incident_type_service.get_by_name(
        db_session=db_session, name=incident.incident_type.name
    )
    if not incident_type_data.plugin_metadata:
        incident_type_data.plugin_metadata = {}

    update_incident_ticket(
        db_session,
        incident.ticket.resource_id,
        title=incident.title,
        description=incident.description,
        incident_type=incident.incident_type.name,
        priority=incident.incident_priority.name,
        status=incident.status,
        commander_email=incident.commander.email,
        reporter_email=incident.reporter.email,
        conversation_weblink=incident.conversation.weblink,
        document_weblink=incident_document["weblink"],
        storage_weblink=incident.storage.weblink,
        conference_weblink=incident.conference.weblink,
        visibility=incident.visibility,
        incident_type_plugin_metadata=incident_type_data.plugin_metadata,
    )

    # we update the investigation document
    update_document(
        incident_document["id"],
        incident.name,
        incident.incident_priority.name,
        incident.status,
        incident.incident_type.name,
        incident.title,
        incident.description,
        incident.commander.name,
        incident.conversation.weblink,
        incident_document["weblink"],
        incident.storage.weblink,
        incident.ticket.weblink,
        incident.conference.weblink,
        incident.conference.conference_challenge,
    )

    for participant in incident.participants:
        # we announce the participant in the conversation
        send_incident_participant_announcement_message(
            participant.individual.email, incident.id, db_session
        )

        # we send the welcome messages to the participant
        send_incident_welcome_participant_messages(
            participant.individual.email, incident.id, db_session
        )

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Participants announced and welcome messages sent",
        incident_id=incident.id,
    )

    if incident.visibility == Visibility.open:
        send_incident_notifications(incident, db_session)
        event_service.log(
            db_session=db_session,
            source="Dispatch Core App",
            description="Incident notifications sent",
            incident_id=incident.id,
        )


@background_task
def incident_active_flow(incident_id: int, command: Optional[dict] = None, db_session=None):
    """Runs the incident active flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we remind the incident commander to write a status report
    send_incident_status_report_reminder(incident)

    # we update the status of the external ticket
    incident_type_data = incident_type_service.get_by_name(
        db_session=db_session, name=incident.incident_type.name
    )
    if not incident_type_data.plugin_metadata:
        incident_type_data.plugin_metadata = {}

    update_incident_ticket(
        db_session,
        incident.ticket.resource_id,
        incident_type=incident.incident_type.name,
        status=IncidentStatus.active.lower(),
        incident_type_plugin_metadata=incident_type_data.plugin_metadata,
    )


@background_task
def incident_stable_flow(incident_id: int, command: Optional[dict] = None, db_session=None):
    """Runs the incident stable flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we set the stable time
    incident.stable_at = datetime.utcnow()

    # we remind the incident commander to write a status report
    send_incident_status_report_reminder(incident)

    # we update the incident cost
    incident_cost = incident_service.calculate_cost(incident_id, db_session)

    # we update the external ticket
    incident_type_data = incident_type_service.get_by_name(
        db_session=db_session, name=incident.incident_type.name
    )
    if not incident_type_data.plugin_metadata:
        incident_type_data.plugin_metadata = {}

    update_incident_ticket(
        db_session,
        incident.ticket.resource_id,
        status=IncidentStatus.stable.lower(),
        cost=incident_cost,
        incident_type_plugin_metadata=incident_type_data.plugin_metadata,
    )

    incident_review_document = get_document(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
    )

    if not incident_review_document:
        storage_plugin = plugins.get(INCIDENT_PLUGIN_STORAGE_SLUG)

        # we create a copy of the incident review document template and we move it to the incident storage
        incident_review_document_name = f"{incident.name} - Post Incident Review Document"
        incident_review_document = storage_plugin.copy_file(
            team_drive_id=incident.storage.resource_id,
            file_id=INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID,
            name=incident_review_document_name,
        )

        incident_review_document.update(
            {
                "name": incident_review_document_name,
                "resource_type": INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
            }
        )

        storage_plugin.move_file(
            new_team_drive_id=incident.storage.resource_id, file_id=incident_review_document["id"]
        )

        event_service.log(
            db_session=db_session,
            source=storage_plugin.title,
            description="Incident review document added to storage",
            incident_id=incident.id,
        )

        document_in = DocumentCreate(
            name=incident_review_document["name"],
            resource_id=incident_review_document["id"],
            resource_type=incident_review_document["resource_type"],
            weblink=incident_review_document["weblink"],
        )
        incident.documents.append(
            document_service.create(db_session=db_session, document_in=document_in)
        )

        event_service.log(
            db_session=db_session,
            source="Dispatch Core App",
            description="Incident review document added to incident",
            incident_id=incident.id,
        )

        # we get the incident investigation and faq documents
        incident_document = get_document(
            db_session=db_session,
            incident_id=incident_id,
            resource_type=INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
        )

        # we update the incident review document
        update_document(
            incident_review_document["id"],
            incident.name,
            incident.incident_priority.name,
            incident.status,
            incident.incident_type.name,
            incident.title,
            incident.description,
            incident.commander.name,
            incident.conversation.weblink,
            incident_document.weblink,
            incident.storage.weblink,
            incident.ticket.weblink,
        )

        # we send a notification about the incident review document to the conversation
        send_incident_review_document_notification(
            incident.conversation.channel_id, incident_review_document["weblink"]
        )

    db_session.add(incident)
    db_session.commit()


@background_task
def incident_closed_flow(incident_id: int, command: Optional[dict] = None, db_session=None):
    """Runs the incident closed flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we set the closed time
    incident.closed_at = datetime.utcnow()

    # we update the incident cost
    incident_cost = incident_service.calculate_cost(incident_id, db_session)

    # we archive the conversation
    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.archive(incident.conversation.channel_id)

    # we update the external ticket
    incident_type_data = incident_type_service.get_by_name(
        db_session=db_session, name=incident.incident_type.name
    )
    if not incident_type_data.plugin_metadata:
        incident_type_data.plugin_metadata = {}

    update_incident_ticket(
        db_session,
        incident.ticket.resource_id,
        status=IncidentStatus.closed.lower(),
        cost=incident_cost,
        incident_type_plugin_metadata=incident_type_data.plugin_metadata,
    )

    if incident.visibility == Visibility.open:
        # we archive the artifacts in the storage
        archive_incident_artifacts(incident, db_session)

        # we delete the tactical and notification groups
        delete_participant_groups(incident, db_session)

    # we delete the conference
    delete_conference(incident, db_session)

    db_session.add(incident)
    db_session.commit()


@background_task
def incident_update_flow(
    user_email: str, incident_id: int, previous_incident: IncidentRead, notify=True, db_session=None
):
    """Runs the incident update flow."""
    conversation_topic_change = False

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we load the individual
    individual = individual_service.get_by_email(db_session=db_session, email=user_email)

    if previous_incident.title != incident.title:
        event_service.log(
            db_session=db_session,
            source="Incident Participant",
            description=f'{individual.name} changed the incident title to "{incident.title}"',
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.description != incident.description:
        event_service.log(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident description",
            details={"description": incident.description},
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.incident_type.name != incident.incident_type.name:
        conversation_topic_change = True

        event_service.log(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident type to {incident.incident_type.name}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.incident_priority.name != incident.incident_priority.name:
        conversation_topic_change = True

        event_service.log(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident priority to {incident.incident_priority.name}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.status.value != incident.status:
        conversation_topic_change = True

        event_service.log(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} marked the incident as {incident.status}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if conversation_topic_change:
        # we update the conversation topic
        set_conversation_topic(incident)

    if notify:
        send_incident_update_notifications(incident, previous_incident)

    # we get the incident document
    incident_document = get_document(
        db_session=db_session,
        incident_id=incident_id,
        resource_type=INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    )

    # we update the external ticket
    incident_type_data = incident_type_service.get_by_name(
        db_session=db_session, name=incident.incident_type.name
    )
    if not incident_type_data.plugin_metadata:
        incident_type_data.plugin_metadata = {}

    update_incident_ticket(
        db_session,
        incident.ticket.resource_id,
        title=incident.title,
        description=incident.description,
        incident_type=incident.incident_type.name,
        priority=incident.incident_priority.name,
        commander_email=incident.commander.email,
        conversation_weblink=incident.conversation.weblink,
        conference_weblink=incident.conference.weblink,
        document_weblink=incident_document.weblink,
        storage_weblink=incident.storage.weblink,
        visibility=incident.visibility,
        incident_type_plugin_metadata=incident_type_data.plugin_metadata,
    )

    log.debug(f"Updated the external ticket {incident.ticket.resource_id}.")

    # get the incident participants based on incident type and priority
    individual_participants, team_participants = get_incident_participants(incident, db_session)

    # lets not attempt to add new participants for non-active incidents (it's confusing)
    if incident.status == IncidentStatus.active:
        # we add the individuals as incident participants
        for individual in individual_participants:
            incident_add_or_reactivate_participant_flow(
                individual.email, incident.id, db_session=db_session
            )

    # we get the notification group
    notification_group = group_service.get_by_incident_id_and_resource_type(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_RESOURCE_NOTIFICATIONS_GROUP,
    )
    team_participant_emails = [x.email for x in team_participants]

    # we add the team distributions lists to the notifications group
    group_plugin = plugins.get(INCIDENT_PLUGIN_GROUP_SLUG)
    group_plugin.add(notification_group.email, team_participant_emails)

    if previous_incident.status.value != incident.status:
        if incident.status == IncidentStatus.active:
            incident_active_flow(incident_id=incident.id, db_session=db_session)
        elif incident.status == IncidentStatus.stable:
            incident_stable_flow(incident_id=incident.id, db_session=db_session)
        elif incident.status == IncidentStatus.closed:
            if previous_incident.status.value == IncidentStatus.active:
                incident_stable_flow(incident_id=incident.id, db_session=db_session)
            incident_closed_flow(incident_id=incident.id, db_session=db_session)


@background_task
def incident_assign_role_flow(
    assigner_email: str, incident_id: int, assignee_email: str, assignee_role: str, db_session=None
):
    """Runs the incident participant role assignment flow."""
    # we resolve the assigner and assignee's contact information
    contact_plugin = plugins.get(INCIDENT_PLUGIN_CONTACT_SLUG)
    assigner_contact_info = contact_plugin.get(assigner_email)
    assignee_contact_info = contact_plugin.get(assignee_email)

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we get the participant object for the assignee
    assignee_participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=assignee_contact_info["email"]
    )

    if not assignee_participant:
        # The assignee is not a participant. We add them to the incident
        incident_add_or_reactivate_participant_flow(
            assignee_email, incident.id, db_session=db_session
        )

    # we run the participant assign role flow
    result = participant_role_flows.assign_role_flow(
        incident.id, assignee_contact_info, assignee_role, db_session
    )

    if result == "assignee_has_role":
        # NOTE: This is disabled until we can determine the source of the caller
        # we let the assigner know that the assignee already has this role
        # send_incident_participant_has_role_ephemeral_message(
        #    assigner_email, assignee_contact_info, assignee_role, incident
        # )
        return

    if result == "role_not_assigned":
        # NOTE: This is disabled until we can determine the source of the caller
        # we let the assigner know that we were not able to assign the role
        # send_incident_participant_role_not_assigned_ephemeral_message(
        #    assigner_email, assignee_contact_info, assignee_role, incident
        # )
        return

    if assignee_role != ParticipantRoleType.participant:
        # we send a notification to the incident conversation
        send_incident_new_role_assigned_notification(
            assigner_contact_info, assignee_contact_info, assignee_role, incident
        )

    if assignee_role == ParticipantRoleType.incident_commander:
        # we update the conversation topic
        set_conversation_topic(incident)

        # we get the incident document
        incident_document = get_document(
            db_session=db_session,
            incident_id=incident_id,
            resource_type=INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
        )

        # we update the external ticket
        incident_type_data = incident_type_service.get_by_name(
            db_session=db_session, name=incident.incident_type.name
        )
        if not incident_type_data.plugin_metadata:
            incident_type_data.plugin_metadata = {}

        update_incident_ticket(
            db_session,
            incident.ticket.resource_id,
            description=incident.description,
            incident_type=incident.incident_type.name,
            commander_email=incident.commander.email,
            conversation_weblink=incident.conversation.weblink,
            document_weblink=incident_document.weblink,
            storage_weblink=incident.storage.weblink,
            visibility=incident.visibility,
            conference_weblink=incident.conference.weblink,
            incident_type_plugin_metadata=incident_type_data.plugin_metadata,
        )


@background_task
def incident_engage_oncall_flow(
    user_id: str, user_email: str, incident_id: int, action: dict, db_session=None
):
    """Runs the incident engage oncall flow."""
    oncall_service_id = action["submission"]["oncall_service_id"]
    page = action["submission"]["page"]

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we resolve the oncall service
    oncall_service = service_service.get_by_external_id(
        db_session=db_session, external_id=oncall_service_id
    )
    oncall_plugin = plugins.get(oncall_service.type)
    oncall_email = oncall_plugin.get(service_id=oncall_service_id)

    # we add the oncall to the incident
    incident_add_or_reactivate_participant_flow(oncall_email, incident.id, db_session=db_session)

    event_service.log(
        db_session=db_session,
        source=oncall_plugin.title,
        description=f"{user_email} engages oncall service {oncall_service.name}",
        incident_id=incident.id,
    )

    if page == "Yes":
        # we page the oncall
        oncall_plugin.page(oncall_service_id, incident.name, incident.title, incident.description)

        event_service.log(
            db_session=db_session,
            source=oncall_plugin.title,
            description=f"{oncall_service.name} on-call paged",
            incident_id=incident.id,
        )


@background_task
def incident_add_or_reactivate_participant_flow(
    user_email: str,
    incident_id: int,
    role: ParticipantRoleType = None,
    event: dict = None,
    db_session=None,
):
    """Runs the add or reactivate incident participant flow."""
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    if participant:
        if participant.is_active:
            log.debug(f"{user_email} is already an active participant.")
        else:
            # we reactivate the participant
            reactivated = participant_flows.reactivate_participant(
                user_email, incident_id, db_session
            )

            if reactivated:
                # we add the participant to the conversation
                add_participant_to_conversation(user_email, incident_id, db_session)

                # we announce the participant in the conversation
                send_incident_participant_announcement_message(user_email, incident_id, db_session)

                # we send the welcome messages to the participant
                send_incident_welcome_participant_messages(user_email, incident_id, db_session)
    else:
        # we add the participant to the incident
        participant = participant_flows.add_participant(
            user_email, incident_id, db_session, role=role
        )

        if participant:
            # we add the participant to the tactical group
            add_participant_to_tactical_group(user_email, incident_id)

            # we add the participant to the conversation
            add_participant_to_conversation(user_email, incident_id, db_session)

            # we announce the participant in the conversation
            send_incident_participant_announcement_message(user_email, incident_id, db_session)

            # we send the welcome messages to the participant
            send_incident_welcome_participant_messages(user_email, incident_id, db_session)


@background_task
def incident_remove_participant_flow(
    user_email: str, incident_id: int, event: dict = None, db_session=None
):
    """Runs the remove participant flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if user_email == incident.commander.email:
        # we add the incident commander to the conversation again
        add_participant_to_conversation(user_email, incident_id, db_session)

        # we send a notification to the channel
        send_incident_commander_readded_notification(incident_id, db_session)
    else:
        # we remove the participant from the incident
        participant_flows.remove_participant(user_email, incident_id, db_session)


@background_task
def incident_list_resources_flow(incident_id: int, command: Optional[dict] = None, db_session=None):
    """Runs the list incident resources flow."""
    # we send the list of resources to the participant
    send_incident_resources_ephemeral_message_to_participant(
        command["user_id"], incident_id, db_session
    )
