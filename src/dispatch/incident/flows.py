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
    INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_SHEET,
    INCIDENT_RESOURCE_NOTIFICATIONS_GROUP,
    INCIDENT_RESOURCE_TACTICAL_GROUP,
    INCIDENT_STORAGE_FOLDER_ID,
    INCIDENT_STORAGE_OPEN_ON_CLOSE,
)

from dispatch.conference import service as conference_service
from dispatch.conference.models import ConferenceCreate
from dispatch.conversation import service as conversation_service
from dispatch.conversation.models import ConversationCreate
from dispatch.database import SessionLocal, resolve_attr
from dispatch.decorators import background_task
from dispatch.document import service as document_service
from dispatch.document.models import DocumentCreate
from dispatch.enums import Visibility
from dispatch.event import service as event_service
from dispatch.group import service as group_service
from dispatch.group.models import GroupCreate
from dispatch.incident import service as incident_service
from dispatch.incident.models import IncidentRead
from dispatch.incident_type import service as incident_type_service
from dispatch.individual import service as individual_service
from dispatch.individual.models import IndividualContact
from dispatch.participant import flows as participant_flows
from dispatch.participant import service as participant_service
from dispatch.participant.models import Participant
from dispatch.participant_role import flows as participant_role_flows
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.base import plugins
from dispatch.report.enums import ReportTypes
from dispatch.report.messaging import send_incident_report_reminder
from dispatch.service import service as service_service
from dispatch.storage import service as storage_service
from dispatch.ticket import service as ticket_service
from dispatch.ticket.models import TicketCreate

from .messaging import (
    get_suggested_document_items,
    send_incident_closed_information_review_reminder,
    send_incident_commander_readded_notification,
    send_incident_new_role_assigned_notification,
    send_incident_notifications,
    send_incident_participant_announcement_message,
    send_incident_rating_feedback_message,
    send_incident_resources_ephemeral_message_to_participant,
    send_incident_review_document_notification,
    send_incident_suggested_reading_messages,
    send_incident_update_notifications,
    send_incident_welcome_participant_messages,
)
from .models import Incident, IncidentStatus


log = logging.getLogger(__name__)


def get_incident_participants(incident: Incident, db_session: SessionLocal):
    """Get additional incident participants based on priority, type, and description."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="participant")
    individual_contacts = []
    team_contacts = []
    if plugin:
        individual_contacts, team_contacts = plugin.instance.get(
            incident.incident_type,
            incident.incident_priority,
            incident.description,
            db_session=db_session,
        )

        event_service.log(
            db_session=db_session,
            source=plugin.title,
            description="Incident participants resolved",
            incident_id=incident.id,
        )

    return individual_contacts, team_contacts


def create_incident_ticket(incident: Incident, db_session: SessionLocal):
    """Create an external ticket for tracking."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="ticket")
    if plugin:
        title = incident.title
        if incident.visibility == Visibility.restricted:
            title = incident.incident_type.name

        incident_type_plugin_metadata = incident_type_service.get_by_name(
            db_session=db_session, name=incident.incident_type.name
        ).get_meta(plugin.slug)

        ticket = plugin.instance.create(
            incident.id,
            title,
            incident.incident_type.name,
            incident.incident_priority.name,
            incident.commander.email,
            incident.reporter.email,
            incident_type_plugin_metadata,
        )
        ticket.update({"resource_type": plugin.slug})

        event_service.log(
            db_session=db_session,
            source=plugin.title,
            description="Ticket created",
            incident_id=incident.id,
        )

        return ticket


def update_external_incident_ticket(
    incident: Incident,
    db_session: SessionLocal,
):
    """Update external incident ticket."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="ticket")
    if not plugin:
        log.warning("External ticket not updated, no ticket plugin enabled.")
        return

    title = incident.title
    description = incident.description
    if incident.visibility == Visibility.restricted:
        title = description = incident.incident_type.name

    incident_type_plugin_metadata = incident_type_service.get_by_name(
        db_session=db_session, name=incident.incident_type.name
    ).get_meta(plugin.slug)

    plugin.instance.update(
        incident.ticket.resource_id,
        title,
        description,
        incident.incident_type.name,
        incident.incident_priority.name,
        incident.status.lower(),
        incident.commander.email,
        incident.reporter.email,
        resolve_attr(incident, "conversation.weblink"),
        resolve_attr(incident, "incident_document.weblink"),
        resolve_attr(incident, "storage.weblink"),
        resolve_attr(incident, "conference.weblink"),
        incident.cost,
        incident_type_plugin_metadata=incident_type_plugin_metadata,
    )

    log.debug(f"Updated the external ticket {incident.ticket.resource_id}.")


def create_participant_groups(
    incident: Incident,
    direct_participants: List[Any],
    indirect_participants: List[Any],
    db_session: SessionLocal,
):
    """Create external participant groups."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="participant-group")

    group_name = f"{incident.name}"
    notification_group_name = f"{group_name}-notifications"

    direct_participant_emails = [x.email for x in direct_participants]
    tactical_group = plugin.instance.create(
        group_name, direct_participant_emails
    )  # add participants to core group

    indirect_participant_emails = [x.email for x in indirect_participants]
    indirect_participant_emails.append(
        tactical_group["email"]
    )  # add all those already in the tactical group
    notification_group = plugin.instance.create(
        notification_group_name, indirect_participant_emails
    )

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
        source=plugin.title,
        description="Tactical and notification groups created",
        incident_id=incident.id,
    )

    return tactical_group, notification_group


def delete_participant_groups(incident: Incident, db_session: SessionLocal):
    """Deletes the external participant groups."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="participant-group")
    plugin.instance.delete(email=incident.tactical_group.email)
    plugin.instance.delete(email=incident.notifications_group.email)

    event_service.log(
        db_session=db_session,
        source=plugin.title,
        description="Tactical and notification groups deleted",
        incident_id=incident.id,
    )


def create_conference(incident: Incident, participants: List[str], db_session: SessionLocal):
    """Create external conference room."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conference")
    conference = plugin.instance.create(incident.name, participants=participants)

    conference.update({"resource_type": plugin.slug, "resource_id": conference["id"]})

    event_service.log(
        db_session=db_session,
        source=plugin.title,
        description="Incident conference created",
        incident_id=incident.id,
    )

    return conference


def delete_conference(incident: Incident, db_session: SessionLocal):
    """Deletes the conference."""
    conference = conference_service.get_by_incident_id(
        db_session=db_session, incident_id=incident.id
    )
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conference")
    plugin.instance.delete(conference.conference_id)

    event_service.log(
        db_session=db_session,
        source=plugin.title,
        description="Incident conference deleted",
        incident_id=incident.id,
    )


def create_incident_storage(
    incident: Incident, participant_group_emails: List[str], db_session: SessionLocal
):
    """Create an external file store for incident storage."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="storage")
    storage = plugin.instance.create_file(
        INCIDENT_STORAGE_FOLDER_ID, incident.name, participant_group_emails
    )
    storage.update({"resource_type": plugin.slug, "resource_id": storage["id"]})
    return storage


def create_collaboration_documents(incident: Incident, db_session: SessionLocal):
    """Create external collaboration document."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="storage")

    collab_documents = []
    document_name = f"{incident.name} - Incident Document"

    if plugin:
        # TODO can we make move and copy in one api call? (kglisson)
        # NOTE: make template documents optional
        if incident.incident_type.template_document:
            document = plugin.instance.copy_file(
                incident.storage.resource_id,
                incident.incident_type.template_document.resource_id,
                document_name,
            )
            plugin.instance.move_file(incident.storage.resource_id, document["id"])

            # TODO this logic should probably be pushed down into the plugins i.e. making them return
            # the fields we expect instead of re-mapping. (kglisson)
            document.update(
                {
                    "name": document_name,
                    "resource_type": INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
                    "resource_id": document["id"],
                }
            )

            collab_documents.append(document)

            event_service.log(
                db_session=db_session,
                source=plugin.title,
                description="Incident investigation document created",
                incident_id=incident.id,
            )

        sheet = None
        template = document_service.get_incident_investigation_sheet_template(db_session=db_session)
        if template:
            sheet_name = f"{incident.name} - Incident Tracking Sheet"
            sheet = plugin.instance.copy_file(
                incident.storage.resource_id, template.resource_id, sheet_name
            )
            plugin.instance.move_file(incident.storage.resource_id, sheet["id"])

            sheet.update(
                {
                    "name": sheet_name,
                    "resource_type": INCIDENT_RESOURCE_INVESTIGATION_SHEET,
                    "resource_id": sheet["id"],
                }
            )
            collab_documents.append(sheet)
            event_service.log(
                db_session=db_session,
                source=plugin.title,
                description="Incident investigation sheet created",
                incident_id=incident.id,
            )

        plugin.instance.create_file(incident.storage.resource_id, "logs")
        plugin.instance.create_file(incident.storage.resource_id, "screengrabs")

    return collab_documents


def create_conversation(incident: Incident, participants: List[str], db_session: SessionLocal):
    """Create external communication conversation."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    conversation = plugin.instance.create(incident.name, participants)
    conversation.update({"resource_type": plugin.slug, "resource_id": conversation["name"]})

    event_service.log(
        db_session=db_session,
        source=plugin.title,
        description="Incident conversation created",
        incident_id=incident.id,
    )

    return conversation


def set_conversation_topic(incident: Incident, db_session: SessionLocal):
    """Sets the conversation topic."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    conversation_topic = f":helmet_with_white_cross: {incident.commander.name} - Type: {incident.incident_type.name} - Priority: {incident.incident_priority.name} - Status: {incident.status}"
    plugin.instance.set_topic(incident.conversation.channel_id, conversation_topic)


def add_participant_to_conversation(
    participant_email: str, incident_id: int, db_session: SessionLocal
):
    """Adds a participant to the conversation."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    plugin.instance.add(incident.conversation.channel_id, [participant_email])


def add_participant_to_tactical_group(user_email: str, incident_id: int, db_session: SessionLocal):
    """Adds participant to the tactical group."""
    # we get the tactical group
    tactical_group = group_service.get_by_incident_id_and_resource_type(
        db_session=db_session,
        incident_id=incident_id,
        resource_type=INCIDENT_RESOURCE_TACTICAL_GROUP,
    )
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="participant-group")
    if plugin:
        plugin.instance.add(tactical_group.email, [user_email])


@background_task
def incident_create_stable_flow(*, incident_id: int, checkpoint: str = None, db_session=None):
    """Creates all resources necessary when an incident is created as 'stable'."""
    incident_create_flow(incident_id=incident_id, db_session=db_session)
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    incident_stable_status_flow(incident=incident, db_session=db_session)


@background_task
def incident_create_closed_flow(*, incident_id: int, checkpoint: str = None, db_session=None):
    """Creates all resources necessary when an incident is created as 'closed'."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we set the stable and close times to the reported time
    incident.stable_at = incident.closed_at = incident.reported_at

    ticket = create_incident_ticket(incident, db_session)
    if ticket:
        incident.ticket = ticket_service.create(
            db_session=db_session, ticket_in=TicketCreate(**ticket)
        )

        incident.name = ticket["resource_id"]
        update_external_incident_ticket(incident, db_session)

    db_session.add(incident)
    db_session.commit()


# TODO create some ability to checkpoint
# We could use the model itself as the checkpoint, commiting resources as we go
# Then checking for the existence of those resources before creating them for
# this incident.
@background_task
def incident_create_flow(*, incident_id: int, checkpoint: str = None, db_session=None):
    """Creates all resources required for new incidents."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # create the incident ticket
    ticket = create_incident_ticket(incident, db_session)
    if ticket:
        incident.ticket = ticket_service.create(
            db_session=db_session, ticket_in=TicketCreate(**ticket)
        )

        # we set the incident name
        incident.name = ticket["resource_id"]

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

    # we create the participant groups (tactical and notification)
    individual_participants = [x.individual for x in incident.participants]
    participant_emails = [x.individual.email for x in incident.participants]

    group_plugin = plugin_service.get_active(db_session=db_session, plugin_type="participant-group")
    tactical_group = None
    notification_group = None
    if group_plugin:
        try:
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
                incident.groups.append(
                    group_service.create(db_session=db_session, group_in=group_in)
                )

            event_service.log(
                db_session=db_session,
                source="Dispatch Core App",
                description="Tactical and notification groups added to incident",
                incident_id=incident.id,
            )
        except Exception as e:
            event_service.log(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of tactical and notification groups failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

    storage_plugin = plugin_service.get_active(db_session=db_session, plugin_type="storage")
    if storage_plugin:
        # we create storage resource
        try:
            if group_plugin:
                storage = create_incident_storage(
                    incident, [tactical_group["email"], notification_group["email"]], db_session
                )
            else:
                # we don't have a group so add participants directly
                storage = create_incident_storage(incident, participant_emails, db_session)

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
        except Exception as e:
            event_service.log(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of incident storage failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

        # we create collaboration documents, don't fail the whole flow if this fails
        try:
            collab_documents = create_collaboration_documents(incident, db_session)

            for d in collab_documents:
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
        except Exception as e:
            event_service.log(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of incident documents failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

    conference_plugin = plugin_service.get_active(db_session=db_session, plugin_type="conference")
    if conference_plugin:
        try:
            participants = participant_emails

            if group_plugin:
                # we use the tactical group email if the group plugin is enabled
                participants = [tactical_group["email"]]

            conference = create_conference(incident, participants, db_session)

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
        except Exception as e:
            event_service.log(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of incident conference failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

    # we create the conversation for real-time communications

    conversation_plugin = plugin_service.get_active(
        db_session=db_session, plugin_type="conversation"
    )
    if conversation_plugin:
        try:
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

            # we set the conversation topic
            set_conversation_topic(incident, db_session)
        except Exception as e:
            event_service.log(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of incident conversation failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

    db_session.add(incident)
    db_session.commit()

    # we update the incident ticket
    update_external_incident_ticket(incident, db_session)

    # we update the investigation document
    document_plugin = plugin_service.get_active(db_session=db_session, plugin_type="document")
    if document_plugin:
        if incident.incident_document:
            try:
                document_plugin.instance.update(
                    incident.incident_document.resource_id,
                    name=incident.name,
                    priority=incident.incident_priority.name,
                    status=incident.status,
                    type=incident.incident_type.name,
                    title=incident.title,
                    description=incident.description,
                    commander_fullname=incident.commander.name,
                    conversation_weblink=resolve_attr(incident, "conversation.weblink"),
                    document_weblink=resolve_attr(incident, "incident_document.weblink"),
                    storage_weblink=resolve_attr(incident, "storage.weblink"),
                    ticket_weblink=resolve_attr(incident, "ticket.weblink"),
                    conference_weblink=resolve_attr(incident, "conference.weblink"),
                    conference_challenge=resolve_attr(incident, "conference.challenge"),
                )
            except Exception as e:
                event_service.log(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description=f"Incident documents rendering failed. Reason: {e}",
                    incident_id=incident.id,
                )
                log.exception(e)

    if incident.visibility == Visibility.open:
        send_incident_notifications(incident, db_session)
        event_service.log(
            db_session=db_session,
            source="Dispatch Core App",
            description="Incident notifications sent",
            incident_id=incident.id,
        )

    suggested_document_items = get_suggested_document_items(incident.id, db_session)

    for participant in incident.participants:
        # we announce the participant in the conversation
        # should protect ourselves from failures of any one participant
        try:
            send_incident_participant_announcement_message(
                participant.individual.email, incident.id, db_session
            )

            # we send the welcome messages to the participant
            send_incident_welcome_participant_messages(
                participant.individual.email, incident.id, db_session
            )

            send_incident_suggested_reading_messages(
                incident.id, suggested_document_items, participant.individual.email, db_session
            )

        except Exception as e:
            log.exception(e)

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Participants announced and welcome messages sent",
        incident_id=incident.id,
    )


def incident_active_status_flow(incident: Incident, db_session=None):
    """Runs the incident active flow."""
    # we un-archive the conversation
    convo_plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if convo_plugin:
        convo_plugin.instance.unarchive(incident.conversation.channel_id)


def incident_stable_status_flow(incident: Incident, db_session=None):
    """Runs the incident stable flow."""
    # we set the stable time
    incident.stable_at = datetime.utcnow()

    # set time immediately
    db_session.add(incident)
    db_session.commit()

    if incident.incident_review_document:
        log.debug("Incident review document already created... skipping creation.")
        return

    storage_plugin = plugin_service.get_active(db_session=db_session, plugin_type="storage")
    if not storage_plugin:
        log.warning("Incident review document not created, no storage plugin enabled.")
        return

    # we create a copy of the incident review document template and we move it to the incident storage
    incident_review_document_name = f"{incident.name} - Post Incident Review Document"
    template = document_service.get_incident_review_template(db_session=db_session)

    # incident review document is optional
    if not template:
        log.warning("No incident review template specificed.")
        return

    incident_review_document = storage_plugin.instance.copy_file(
        folder_id=incident.storage.resource_id,
        file_id=template.resource_id,
        name=incident_review_document_name,
    )

    incident_review_document.update(
        {
            "name": incident_review_document_name,
            "resource_type": INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
        }
    )

    storage_plugin.instance.move_file(
        new_folder_id=incident.storage.resource_id,
        file_id=incident_review_document["id"],
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

    # we update the incident review document
    document_plugin = plugin_service.get_active(db_session=db_session, plugin_type="document")
    if document_plugin:
        document_plugin.instance.update(
            incident.incident_review_document.resource_id,
            name=incident.name,
            priority=incident.incident_priority.name,
            status=incident.status,
            type=incident.incident_type.name,
            title=incident.title,
            description=incident.description,
            commander_fullname=incident.commander.name,
            conversation_weblink=resolve_attr(incident, "conversation.weblink"),
            document_weblink=resolve_attr(incident, "incident_document.weblink"),
            storage_weblink=resolve_attr(incident, "storage.weblink"),
            ticket_weblink=resolve_attr(incident, "ticket.weblink"),
            conference_weblink=resolve_attr(incident, "conference.weblink"),
            conference_challenge=resolve_attr(incident, "conference.challenge"),
        )
    else:
        log.warning("No document plugin enabled, could not update template.")

    # we send a notification about the incident review document to the conversation
    send_incident_review_document_notification(
        incident.conversation.channel_id,
        incident.incident_review_document.weblink,
        db_session,
    )

    db_session.add(incident)
    db_session.commit()


def incident_closed_status_flow(incident: Incident, db_session=None):
    """Runs the incident closed flow."""
    # we set the closed time
    incident.closed_at = datetime.utcnow()

    # set time immediately
    db_session.add(incident)
    db_session.commit()

    # we archive the conversation
    convo_plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if convo_plugin:
        convo_plugin.instance.archive(incident.conversation.channel_id)

    if INCIDENT_STORAGE_OPEN_ON_CLOSE:
        # incidents with restricted visibility are never opened
        if incident.visibility == Visibility.open:
            # add organization wide permission
            storage_plugin = plugin_service.get_active(db_session=db_session, plugin_type="storage")
            if storage_plugin:
                storage_plugin.instance.open(incident.storage.resource_id)

    # we send a direct message to the incident commander asking to review
    # the incident's information and to tag the incident if appropiate
    send_incident_closed_information_review_reminder(incident, db_session)

    # we send a direct message to all participants asking them
    # to rate and provide feedback about the incident
    send_incident_rating_feedback_message(incident, db_session)


def conversation_topic_dispatcher(
    incident: Incident,
    previous_incident: dict,
    individual: IndividualContact,
    db_session: SessionLocal,
):
    """Determines if the conversation topic needs to be updated."""
    conversation_topic_change = False
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
        if incident.status != IncidentStatus.closed:
            set_conversation_topic(incident, db_session)


def status_flow_dispatcher(
    incident: Incident,
    current_status: IncidentStatus,
    previous_status: IncidentStatus,
    db_session=SessionLocal,
):
    """Runs the correct flows depending on the incident's current and previous status."""
    # we have a currently active incident
    if current_status == IncidentStatus.active:
        # re-activate incident
        incident_active_status_flow(incident=incident, db_session=db_session)
        send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)

    # we currently have a stable incident
    elif current_status == IncidentStatus.stable:
        if previous_status == IncidentStatus.active:
            incident_stable_status_flow(incident=incident, db_session=db_session)
        elif previous_status == IncidentStatus.closed:
            incident_active_status_flow(incident=incident, db_session=db_session)
            incident_stable_status_flow(incident=incident, db_session=db_session)
        send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)

    # we currently have a closed incident
    elif current_status == IncidentStatus.closed:
        if previous_status == IncidentStatus.active:
            incident_stable_status_flow(incident=incident, db_session=db_session)
            incident_closed_status_flow(incident=incident, db_session=db_session)

        elif previous_status == IncidentStatus.stable:
            incident_closed_status_flow(incident=incident, db_session=db_session)


def resolve_incident_participants(incident: Incident, db_session: SessionLocal):
    """Controls how and when participants are resolved and associated with an incident."""
    # only add resolve new partcipants in some situations
    if incident.status == IncidentStatus.active:
        # get the incident participants based on incident type and priority
        individual_participants, team_participants = get_incident_participants(incident, db_session)

        # lets not attempt to add new participants for non-active incidents (it's confusing)
        if incident.status == IncidentStatus.active:
            # we add the individuals as incident participants
            for individual in individual_participants:
                incident_add_or_reactivate_participant_flow(
                    individual.email, incident.id, db_session=db_session
                )

        team_participant_emails = [x.email for x in team_participants]

        # we add the team distributions lists to the notifications group
        group_plugin = plugin_service.get_active(
            db_session=db_session, plugin_type="participant-group"
        )
        if group_plugin:
            group_plugin.instance.add(incident.notifications_group.email, team_participant_emails)


@background_task
def incident_update_flow(
    user_email: str, incident_id: int, previous_incident: IncidentRead, notify=True, db_session=None
):
    """Runs the incident update flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we load the individual
    individual = individual_service.get_by_email(db_session=db_session, email=user_email)

    # run whatever flows we need
    status_flow_dispatcher(
        incident, incident.status, previous_incident.status.value, db_session=db_session
    )

    conversation_topic_dispatcher(incident, previous_incident, individual, db_session=db_session)

    # we update the external ticket
    update_external_incident_ticket(incident, db_session)

    # add new folks to the incident if appropriate
    resolve_incident_participants(incident, db_session)

    if notify:
        send_incident_update_notifications(incident, previous_incident, db_session)


@background_task
def incident_assign_role_flow(
    assigner_email: str, incident_id: int, assignee_email: str, assignee_role: str, db_session=None
):
    """Runs the incident participant role assignment flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we get the participant object for the assignee
    assignee_participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=assignee_email
    )

    if not assignee_participant:
        # The assignee is not a participant. We add them to the incident
        incident_add_or_reactivate_participant_flow(
            assignee_email, incident.id, db_session=db_session
        )

    # we run the participant assign role flow
    result = participant_role_flows.assign_role_flow(
        incident.id, assignee_email, assignee_role, db_session
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
        # we resolve the assigner and assignee's contact information
        plugin = plugin_service.get_active(db_session=db_session, plugin_type="contact")

        if plugin:
            assigner_contact_info = plugin.instance.get(assigner_email, db_session=db_session)
            assignee_contact_info = plugin.instance.get(assignee_email, db_session=db_session)
        else:
            assigner_contact_info = {
                "email": assigner_email,
                "fullname": "Unknown",
                "weblink": None,
            }
            assignee_contact_info = {
                "email": assignee_email,
                "fullname": "Unknown",
                "weblink": None,
            }

        # we send a notification to the incident conversation
        send_incident_new_role_assigned_notification(
            assigner_contact_info, assignee_contact_info, assignee_role, incident, db_session
        )

    if assignee_role == ParticipantRoleType.incident_commander:
        # we update the conversation topic
        set_conversation_topic(incident, db_session)

        # we update the external ticket
        update_external_incident_ticket(incident, db_session)


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

    # we load the individual
    individual = individual_service.get_by_email(db_session=db_session, email=user_email)

    event_service.log(
        db_session=db_session,
        source=oncall_plugin.title,
        description=f"{individual.name} engages oncall service {oncall_service.name}",
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
) -> Participant:
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

        # we add the participant to the tactical group
        add_participant_to_tactical_group(user_email, incident_id, db_session)

        # we add the participant to the conversation
        add_participant_to_conversation(user_email, incident_id, db_session)

        # we announce the participant in the conversation
        send_incident_participant_announcement_message(user_email, incident_id, db_session)

        # we send the welcome messages to the participant
        send_incident_welcome_participant_messages(user_email, incident_id, db_session)

        # we send a suggested reading message to the participant
        suggested_document_items = get_suggested_document_items(incident_id, db_session)
        send_incident_suggested_reading_messages(
            incident_id, suggested_document_items, user_email, db_session
        )

    return participant


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
