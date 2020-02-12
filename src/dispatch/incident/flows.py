"""
.. module: dispatch.incident.flows
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""
import logging
from typing import Any, List, Optional

from dispatch.config import (
    INCIDENT_CONTACT_PLUGIN_SLUG,
    INCIDENT_CONVERSATION_SLUG,
    INCIDENT_DOCUMENT_FAQ_DOCUMENT_SLUG,
    INCIDENT_DOCUMENT_INCIDENT_REVIEW_DOCUMENT_SLUG,
    INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
    INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID,
    INCIDENT_DOCUMENT_INVESTIGATION_SHEET_SLUG,
    INCIDENT_DOCUMENT_RESOLVER_PLUGIN_SLUG,
    INCIDENT_DOCUMENT_SLUG,
    INCIDENT_FAQ_DOCUMENT_ID,
    INCIDENT_GROUP_SLUG,
    INCIDENT_NOTIFICATIONS_GROUP_SLUG,
    INCIDENT_PARTICIPANT_PLUGIN_SLUG,
    INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID_SLUG,
    INCIDENT_STORAGE_DRIVE_ID_SLUG,
    INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID_SLUG,
    INCIDENT_STORAGE_SLUG,
    INCIDENT_TACTICAL_GROUP_SLUG,
    INCIDENT_TICKET_PLUGIN_SLUG,
)
from dispatch.conversation import service as conversation_service
from dispatch.decorators import background_task
from dispatch.document import service as document_service
from dispatch.document.models import DocumentCreate
from dispatch.document.service import get_by_incident_id_and_resource_type as get_document
from dispatch.group import service as group_service
from dispatch.group.service import get_by_incident_id_and_resource_type as get_group
from dispatch.incident import service as incident_service
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_priority.models import IncidentPriorityRead
from dispatch.incident_type import service as incident_type_service
from dispatch.incident_type.models import IncidentTypeRead
from dispatch.participant import flows as participant_flows
from dispatch.participant import service as participant_service
from dispatch.participant_role import flows as participant_role_flows
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.base import plugins
from dispatch.service import service as service_service
from dispatch.storage import service as storage_service
from dispatch.ticket import service as ticket_service
from dispatch.ticket.models import TicketCreate

from .messaging import (
    send_incident_change_notifications,
    send_incident_commander_readded_notification,
    send_incident_new_role_assigned_notification,
    send_incident_notifications,
    send_incident_participant_announcement_message,
    send_incident_participant_has_role_ephemeral_message,
    send_incident_participant_role_not_assigned_ephemeral_message,
    send_incident_resources_ephemeral_message_to_participant,
    send_incident_review_document_notification,
    send_incident_status_notifications,
    send_incident_welcome_participant_messages,
)
from .models import Incident, IncidentStatus

log = logging.getLogger(__name__)


def get_incident_participants(
    db_session, incident_type: IncidentTypeRead, priority: IncidentPriorityRead, description: str
):
    """Get additional incident participants based on priority, type, and description."""
    p = plugins.get(INCIDENT_PARTICIPANT_PLUGIN_SLUG)
    individual_contacts, team_contacts = p.get(
        incident_type, priority, description, db_session=db_session
    )
    return individual_contacts, team_contacts


def get_incident_documents(
    db_session, incident_type: IncidentTypeRead, priority: IncidentPriorityRead, description: str
):
    """Get additional incident documents based on priority, type, and description."""
    p = plugins.get(INCIDENT_DOCUMENT_RESOLVER_PLUGIN_SLUG)
    documents = p.get(incident_type, priority, description, db_session=db_session)
    return documents


def create_incident_ticket(
    title: str, incident_type: str, priority: str, commander: str, reporter: str
):
    """Create an external ticket for tracking."""
    p = plugins.get(INCIDENT_TICKET_PLUGIN_SLUG)
    ticket = p.create(title, incident_type, priority, commander, reporter)
    ticket.update({"resource_type": INCIDENT_TICKET_PLUGIN_SLUG})
    return ticket


def update_incident_ticket(
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
    labels: List[str] = None,
    cost: str = None,
):
    """Update external incident ticket."""
    p = plugins.get(INCIDENT_TICKET_PLUGIN_SLUG)
    p.update(
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
        labels=labels,
        cost=cost,
    )

    log.debug("The external ticket has been updated.")


def create_participant_groups(
    name: str, indirect_participants: List[Any], direct_participants: List[Any]
):
    """Create external participant groups."""
    p = plugins.get(INCIDENT_GROUP_SLUG)

    group_name = f"{name}"
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
        {"resource_type": INCIDENT_TACTICAL_GROUP_SLUG, "resource_id": tactical_group["id"]}
    )
    notification_group.update(
        {
            "resource_type": INCIDENT_NOTIFICATIONS_GROUP_SLUG,
            "resource_id": notification_group["id"],
        }
    )

    return tactical_group, notification_group


def create_incident_storage(name: str, participant_group_emails: List[str]):
    """Create an external file store for incident storage."""
    p = plugins.get(INCIDENT_STORAGE_SLUG)
    storage = p.create(name, participant_group_emails)
    storage.update({"resource_type": INCIDENT_STORAGE_SLUG, "resource_id": storage["id"]})
    return storage


def create_collaboration_documents(
    name: str, incident_type: str, storage_id: str, template_id: int
):
    """Create external collaboration document."""
    p = plugins.get(INCIDENT_STORAGE_SLUG)

    document_name = f"{name} - Incident Document"

    # TODO can we make move and copy in one api call? (kglisson)
    document = p.copy_file(storage_id, template_id, document_name)
    p.move_file(storage_id, document["id"])

    # NOTE this should be optional
    if INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID:
        sheet_name = f"{name} - Incident Tracking Sheet"
        sheet = p.copy_file(storage_id, INCIDENT_DOCUMENT_INVESTIGATION_SHEET_ID, sheet_name)
        p.move_file(storage_id, sheet["id"])

    p.create_file(storage_id, "logs")
    p.create_file(storage_id, "screengrabs")

    # TODO this logic should probably be pushed down into the plugins i.e. making them return
    # the fields we expect instead of re-mapping. (kglisson)
    document.update(
        {
            "name": document_name,
            "resource_type": INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
            "resource_id": document["id"],
        }
    )
    sheet.update(
        {
            "name": sheet_name,
            "resource_type": INCIDENT_DOCUMENT_INVESTIGATION_SHEET_SLUG,
            "resource_id": sheet["id"],
        }
    )

    return document, sheet


def create_conversation(incident: Incident, participants: List[str]):
    """Create external communication conversation."""
    # we create the conversation
    convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
    conversation = convo_plugin.create(incident.name, participants)

    conversation.update(
        {"resource_type": INCIDENT_CONVERSATION_SLUG, "resource_id": conversation["name"]}
    )

    return conversation


def set_conversation_topic(incident: Incident):
    """Sets the conversation topic."""
    convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
    conversation_topic = f":helmet_with_white_cross: {incident.commander.name} - Type: {incident.incident_type.name} - Priority: {incident.incident_priority.name} - Status: {incident.status}"
    convo_plugin.set_topic(incident.conversation.channel_id, conversation_topic)

    log.debug(f"Conversation topic set to {conversation_topic}.")


def update_document(
    document_id: str,
    name: str,
    priority: str,
    status: str,
    title: str,
    description: str,
    commander_fullname: str,
    conversation_weblink: str,
    document_weblink: str,
    storage_weblink: str,
    ticket_weblink: str,
    form_weblink: str = None,
):
    """Update external collaboration document."""
    p = plugins.get(INCIDENT_DOCUMENT_SLUG)
    p.update(
        document_id,
        name=name,
        priority=priority,
        status=status,
        title=title,
        description=description,
        commander_fullname=commander_fullname,
        conversation_weblink=conversation_weblink,
        document_weblink=document_weblink,
        storage_weblink=storage_weblink,
        ticket_weblink=ticket_weblink,
        form_weblink=form_weblink,
    )

    log.debug("The external collaboration document has been updated.")


def update_incident_status(db_session, incident: Incident, status: str):
    """Updates the status of the incident (active, stable, or closed)."""
    incident.status = status
    db_session.add(incident)
    db_session.commit()

    log.debug(f"The incident has been marked as {status}.")


def add_participant_to_conversation(conversation_id: str, participant_email: str):
    """Adds a participant to the conversation."""
    convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
    convo_plugin.add(conversation_id, [participant_email])


@background_task
def add_participant_to_tactical_group(user_email: str, incident_id: int, db_session=None):
    """Adds participant to the tactical group."""
    # we get the tactical group
    tactical_group = get_group(
        db_session=db_session, incident_id=incident_id, resource_type=INCIDENT_TACTICAL_GROUP_SLUG
    )

    p = plugins.get(INCIDENT_GROUP_SLUG)
    p.add(tactical_group.email, [user_email])

    log.debug(f"{user_email} has been added to tactical group {tactical_group.email}")


# TODO create some ability to checkpoint
# We could use the model itself as the checkpoint, commiting resources as we go
# Then checking for the existence of those resources before creating them for
# this incident.
@background_task
def incident_create_flow(*, incident_id: int, checkpoint: str = None, db_session=None):
    """Creates all resources required for new incidents."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # get the incident participants based on incident type and priority
    individual_participants, team_participants = get_incident_participants(
        db_session, incident.incident_type, incident.incident_priority, incident.description
    )

    # add individuals to incident
    for individual in individual_participants:
        participant_flows.add_participant(
            db_session=db_session, user_email=individual.email, incident_id=incident.id
        )

    log.debug(f"Added {len(individual_participants)} to incident.")

    # create the incident ticket
    ticket = create_incident_ticket(
        incident.title,
        incident.incident_type.name,
        incident.incident_priority.name,
        incident.commander.email,
        incident.reporter.email,
    )

    incident.ticket = ticket_service.create(db_session=db_session, ticket_in=TicketCreate(**ticket))

    log.debug("Added ticket to incident.")

    # we set the incident name
    name = ticket["resource_id"]

    incident.name = name

    log.debug("Added name to incident.")

    # we create the participant groups (tactical and notification)
    tactical_group, notification_group = create_participant_groups(
        name, team_participants, [x.individual for x in incident.participants]
    )

    for g in [tactical_group, notification_group]:
        group = group_service.create(
            db_session=db_session,
            name=g["name"],
            email=g["email"],
            resource_type=g["resource_type"],
            resource_id=g["resource_id"],
            weblink=g["weblink"],
        )
        incident.groups.append(group)

    log.debug("Added groups to incident.")

    # we create storage resource
    storage = create_incident_storage(name, [tactical_group["email"], notification_group["email"]])
    incident.storage = storage_service.create(
        db_session=db_session,
        resource_id=storage["resource_id"],
        resource_type=storage["resource_type"],
        weblink=storage["weblink"],
    )

    # we create the incident documents
    incident_document, incident_sheet = create_collaboration_documents(
        incident.name,
        incident.incident_type.name,
        incident.storage.resource_id,
        incident.incident_type.template_document.resource_id,
    )

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
        "resource_type": INCIDENT_DOCUMENT_FAQ_DOCUMENT_SLUG,
    }

    for d in [incident_document, incident_sheet, faq_document]:
        document_in = DocumentCreate(
            name=d["name"],
            resource_id=d["resource_id"],
            resource_type=d["resource_type"],
            weblink=d["weblink"],
        )
        incident.documents.append(
            document_service.create(db_session=db_session, document_in=document_in)
        )

    log.debug("Added documents to incident.")

    # we create the conversation for real-time communications
    conversation = create_conversation(
        incident, [x.individual.email for x in incident.participants]
    )

    log.debug("Conversation created. Participants and bots added.")

    incident.conversation = conversation_service.create(
        db_session=db_session,
        resource_id=conversation["resource_id"],
        resource_type=conversation["resource_type"],
        weblink=conversation["weblink"],
        channel_id=conversation["id"],
    )
    db_session.add(incident)
    db_session.commit()

    log.debug("Added conversation to incident.")

    # we set the conversation topic
    set_conversation_topic(incident)

    update_incident_ticket(
        incident.ticket.resource_id,
        incident.title,
        incident.description,
        incident.incident_type.name,
        incident.incident_priority.name,
        incident.status,
        incident.commander.email,
        incident.reporter.email,
        incident.conversation.weblink,
        incident_document["weblink"],
        incident.storage.weblink,
    )

    log.debug("Updated incident ticket.")

    update_document(
        incident_document["id"],
        incident.name,
        incident.incident_priority.name,
        incident.status,
        incident.title,
        incident.description,
        incident.commander.name,
        incident.conversation.weblink,
        incident_document["weblink"],
        incident.storage.weblink,
        incident.ticket.weblink,
    )

    log.debug("Updated incident document.")

    for participant in incident.participants:
        # we announce the participant in the conversation
        send_incident_participant_announcement_message(
            participant.individual.email, incident, db_session
        )

        # we send the welcome messages to the participant
        send_incident_welcome_participant_messages(
            participant.individual.email, incident, db_session
        )

    log.debug("Sent incident welcome and announcement notifications.")

    send_incident_notifications(incident, db_session)

    log.debug("Sent incident notifications.")


@background_task
def incident_active_flow(incident_id: int, command: Optional[dict] = None, db_session=None):
    """Runs the incident active flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if incident.status == IncidentStatus.active:
        if command:
            convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
            convo_plugin.send_ephemeral(
                command["channel_id"],
                command["user_id"],
                "Incident Already Active Notification",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "The incident is already active. Aborting command...",
                        },
                    }
                ],
            )
        return

    # we update the status of the incident
    update_incident_status(db_session=db_session, incident=incident, status=IncidentStatus.active)

    log.debug(f"We have updated the status of the incident to {IncidentStatus.active}.")

    # we update the status of the external ticket
    update_incident_ticket(
        incident.ticket.resource_id,
        incident_type=incident.incident_type.name,
        status=IncidentStatus.active.lower(),
    )

    log.debug(f"We have updated the status of the external ticket to {IncidentStatus.active}.")

    # we update the conversation topic
    set_conversation_topic(incident)

    # we send the active notifications
    send_incident_status_notifications(incident, db_session)

    log.debug("We have sent the incident active notifications.")


@background_task
def incident_stable_flow(incident_id: int, command: Optional[dict] = None, db_session=None):
    """Runs the incident stable flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if incident.status == IncidentStatus.stable:
        if command:
            convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
            convo_plugin.send_ephemeral(
                command["channel_id"],
                command["user_id"],
                "Incident Already Stable Notification",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": "The incident is already stable. Aborting command...",
                        },
                    }
                ],
            )
            return

    # we update the status of the incident
    update_incident_status(db_session=db_session, incident=incident, status=IncidentStatus.stable)

    log.debug(f"We have updated the status of the incident to {IncidentStatus.stable}.")

    # we update the incident cost
    incident_cost = incident_service.calculate_cost(incident_id, db_session)

    log.debug(f"We have updated the cost of the incident.")

    # we update the external ticket
    update_incident_ticket(
        incident.ticket.resource_id,
        incident_type=incident.incident_type.name,
        status=IncidentStatus.stable.lower(),
        cost=incident_cost,
    )

    log.debug(f"We have updated the status of the external ticket to {IncidentStatus.stable}.")

    # we update the conversation topic
    set_conversation_topic(incident)

    incident_review_document = get_document(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_DOCUMENT_INCIDENT_REVIEW_DOCUMENT_SLUG,
    )

    if not incident_review_document:
        storage_plugin = plugins.get(INCIDENT_STORAGE_SLUG)

        # we create a copy of the incident review document template and we move it to the incident storage
        incident_review_document_name = f"{incident.name} - Post Incident Review Document"
        incident_review_document = storage_plugin.copy_file(
            team_drive_id=INCIDENT_STORAGE_DRIVE_ID_SLUG,
            file_id=INCIDENT_STORAGE_INCIDENT_REVIEW_FILE_ID_SLUG,
            name=incident_review_document_name,
        )

        incident_review_document.update(
            {
                "name": incident_review_document_name,
                "resource_type": INCIDENT_DOCUMENT_INCIDENT_REVIEW_DOCUMENT_SLUG,
            }
        )

        storage_plugin.move_file(
            new_team_drive_id=incident.storage.resource_id, file_id=incident_review_document["id"]
        )

        log.debug("We have added the incident review document in the incident storage.")

        document_in = DocumentCreate(
            name=incident_review_document["name"],
            resource_id=incident_review_document["id"],
            resource_type=incident_review_document["resource_type"],
            weblink=incident_review_document["weblink"],
        )
        incident.documents.append(
            document_service.create(db_session=db_session, document_in=document_in)
        )

        db_session.add(incident)
        db_session.commit()

        log.debug("We have added the incident review document to the incident.")

        # we get the incident investigation and faq documents
        incident_document = get_document(
            db_session=db_session,
            incident_id=incident_id,
            resource_type=INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
        )

        # we update the incident review document
        update_document(
            incident_review_document["id"],
            incident.name,
            incident.incident_priority.name,
            incident.status,
            incident.title,
            incident.description,
            incident.commander.name,
            incident.conversation.weblink,
            incident_document.weblink,
            incident.storage.weblink,
            incident.ticket.weblink,
        )

        log.debug("We have updated the incident review document.")

        # we send a notification about the incident review document to the conversation
        send_incident_review_document_notification(
            incident.conversation.channel_id, incident_review_document["weblink"]
        )

        log.debug(
            "We have sent a notification about the incident review document to the conversation."
        )

    # we send the stable notifications
    send_incident_status_notifications(incident, db_session)

    log.debug("We have sent the incident stable notifications.")


@background_task
def incident_closed_flow(incident_id: int, command: Optional[dict] = None, db_session=None):
    """Runs the incident closed flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if incident.status == IncidentStatus.active:
        # we run the stable flow and let the user know
        if command:
            convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
            convo_plugin.send_ephemeral(
                command["channel_id"],
                command["user_id"],
                "Mark Incident Stable Notification",
                blocks=[
                    {
                        "type": "section",
                        "text": {"type": "plain_text", "text": "Marking the incident as stable..."},
                    }
                ],
            )
        incident_stable_flow(incident_id, command=command, db_session=db_session)

    # we update the status of the incident
    update_incident_status(db_session=db_session, incident=incident, status=IncidentStatus.closed)
    log.debug(f"We have updated the status of the incident to {IncidentStatus.closed}.")

    # we update the incident cost
    incident_cost = incident_service.calculate_cost(incident_id, db_session)
    log.debug(f"We have updated the cost of the incident.")

    # we archive the conversation
    convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
    convo_plugin.archive(incident.conversation.channel_id)
    log.debug("We have archived the incident conversation.")

    # we send the closed notifications
    send_incident_status_notifications(incident, db_session)
    log.debug("We have sent the incident closed notifications.")

    # we update the external ticket
    update_incident_ticket(
        incident.ticket.resource_id,
        incident_type=incident.incident_type.name,
        status=IncidentStatus.closed.lower(),
        cost=incident_cost,
    )
    log.debug(f"We have updated the status of the external ticket to {IncidentStatus.closed}.")

    # we archive the artifacts in the storage
    storage_plugin = plugins.get(INCIDENT_STORAGE_SLUG)
    storage_plugin.archive(
        source_team_drive_id=incident.storage.resource_id,
        dest_team_drive_id=INCIDENT_STORAGE_ARCHIVAL_FOLDER_ID_SLUG,
        folder_name=incident.name,
    )
    log.debug(
        "We have archived the incident artifacts in the archival folder and re-applied permissions and deleted the source."
    )

    # we get the tactical group
    tactical_group = get_group(
        db_session=db_session, incident_id=incident_id, resource_type=INCIDENT_TACTICAL_GROUP_SLUG
    )

    # we get the notifications group
    notifications_group = get_group(
        db_session=db_session,
        incident_id=incident_id,
        resource_type=INCIDENT_NOTIFICATIONS_GROUP_SLUG,
    )

    group_plugin = plugins.get(INCIDENT_GROUP_SLUG)
    group_plugin.delete(email=tactical_group.email)
    group_plugin.delete(email=notifications_group.email)
    log.debug("We have deleted the notification and tactical groups.")


@background_task
def incident_edit_flow(user_email: str, incident_id: int, action: dict, db_session=None):
    """Runs the incident edit flow."""
    notify = action["submission"]["notify"]
    incident_title = action["submission"]["title"]
    incident_description = action["submission"]["description"]
    incident_type = action["submission"]["type"]
    incident_priority = action["submission"]["priority"]
    incident_visibility = action["submission"]["visibility"]

    conversation_topic_change = False

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we update the incident title
    incident.title = incident_title
    log.debug(f"Updated the incident title to {incident_title}.")

    # we update the incident description
    incident.description = incident_description
    log.debug(f"Updated the incident description to {incident_description}.")

    if incident_type != incident.incident_type.name:
        # we update the incident type
        incident_type_obj = incident_type_service.get_by_name(
            db_session=db_session, name=incident_type
        )
        incident.incident_type_id = incident_type_obj.id

        log.debug(f"Updated the incident type to {incident_type}.")

        conversation_topic_change = True

    if incident_priority != incident.incident_priority.name:
        # we update the incident priority
        incident_priority_obj = incident_priority_service.get_by_name(
            db_session=db_session, name=incident_priority
        )
        incident.incident_priority_id = incident_priority_obj.id

        log.debug(f"Updated the incident priority to {incident_priority}.")

        conversation_topic_change = True

    if incident_visibility != incident.visibility:
        # we update the incident visibility
        incident.visibility = incident_visibility

        log.debug(f"Updated the incident visibility to {incident_visibility}.")

    if notify == "Yes":
        send_incident_change_notifications(
            incident, incident_title, incident_type, incident_priority
        )

    # we commit the changes to the incident
    db_session.add(incident)
    db_session.commit()

    if conversation_topic_change:
        # we update the conversation topic
        set_conversation_topic(incident)

    # we get the incident document
    incident_document = get_document(
        db_session=db_session,
        incident_id=incident_id,
        resource_type=INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
    )

    # we update the external ticket
    update_incident_ticket(
        incident.ticket.resource_id,
        title=incident.title,
        description=incident.description,
        incident_type=incident_type,
        priority=incident_priority,
        commander_email=incident.commander.email,
        conversation_weblink=incident.conversation.weblink,
        document_weblink=incident_document.weblink,
        storage_weblink=incident.storage.weblink,
    )

    log.debug(f"Updated the external ticket {incident.ticket.resource_id}.")

    # get the incident participants based on incident type and priority
    individual_participants, team_participants = get_incident_participants(
        db_session, incident.incident_type, incident.incident_priority, incident.description
    )

    # we add the individuals as incident participants
    for individual in individual_participants:
        incident_add_or_reactivate_participant_flow(
            individual.email, incident.id, db_session=db_session
        )

    # we get the tactical group
    notification_group = get_group(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_NOTIFICATIONS_GROUP_SLUG,
    )
    team_participant_emails = [x.email for x in team_participants]

    # we add the team distributions lists to the notifications group
    group_plugin = plugins.get(INCIDENT_GROUP_SLUG)
    group_plugin.add(notification_group.email, team_participant_emails)

    log.debug(f"Resolved and added new participants to the incident.")


@background_task
def incident_assign_role_flow(assigner_email: str, incident_id: int, action: dict, db_session=None):
    """Runs the incident participant role assignment flow."""
    assignee_user_id = action["submission"]["participant"]
    assignee_role = action["submission"]["role"]

    # we resolve the assignee's email address
    convo_plugin = plugins.get(INCIDENT_CONVERSATION_SLUG)
    assignee_email = convo_plugin.get_participant_email(assignee_user_id)

    # we resolve the assigner and assignee's contact information
    contact_plugin = plugins.get(INCIDENT_CONTACT_PLUGIN_SLUG)
    assigner_contact_info = contact_plugin.get(assigner_email)
    assignee_contact_info = contact_plugin.get(assignee_email)

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we get the participant object for the assignee
    assignee_participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=assignee_contact_info["email"]
    )

    if not assignee_participant:
        # The assignee is not a participant. We add them to the incident with the given role
        incident_add_or_reactivate_participant_flow(
            assignee_email, incident.id, db_session=db_session
        )

    # we run the participant assign role flow
    result = participant_role_flows.assign_role_flow(
        db_session, incident, assignee_contact_info, assignee_role
    )

    if result == "assignee_has_role":
        # we let the assigner know that the assignee already has this role
        send_incident_participant_has_role_ephemeral_message(
            assigner_email, assignee_contact_info, assignee_role, incident
        )
        return

    if result == "role_not_assigned":
        # we let the assigner know that we were not able to assign the role
        send_incident_participant_role_not_assigned_ephemeral_message(
            assigner_email, assignee_contact_info, assignee_role, incident
        )
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
            resource_type=INCIDENT_DOCUMENT_INVESTIGATION_DOCUMENT_SLUG,
        )

        # we update the external ticket
        update_incident_ticket(
            incident.ticket.resource_id,
            description=incident.description,
            incident_type=incident.incident_type.name,
            commander_email=incident.commander.email,
            conversation_weblink=incident.conversation.weblink,
            document_weblink=incident_document.weblink,
            storage_weblink=incident.storage.weblink,
        )


@background_task
def incident_engage_oncall_flow(user_email: str, incident_id: int, action: dict, db_session=None):
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

    if page == "Yes":
        # we page the oncall
        oncall_plugin.page(oncall_service_id, incident.name, incident.title, incident.description)

    log.debug(f"{user_email} has engaged oncall service {oncall_service.name}")


@background_task
def incident_add_or_reactivate_participant_flow(
    user_email: str, incident_id: int, role: ParticipantRoleType = None, db_session=None
):
    """Runs the add or reactivate incident participant flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # We get information about the individual
    contact_plugin = plugins.get(INCIDENT_CONTACT_PLUGIN_SLUG)
    individual_info = contact_plugin.get(user_email)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    if participant:
        if participant.is_active:
            log.debug(f"{individual_info['fullname']} is already an active participant.")
            return
        else:
            # we reactivate the participant
            reactivated = participant_flows.reactivate_participant(
                user_email, incident_id, db_session
            )

            if reactivated:
                # we add the participant to the conversation
                add_participant_to_conversation(incident.conversation.channel_id, user_email)

                # we announce the participant in the conversation
                send_incident_participant_announcement_message(user_email, incident, db_session)

                # we send the welcome messages to the participant
                send_incident_welcome_participant_messages(user_email, incident, db_session)

            return
    else:
        # we add the participant to the incident
        added = participant_flows.add_participant(user_email, incident_id, db_session, role=role)

        if added:
            # we add the participant to the tactical group
            add_participant_to_tactical_group(user_email, incident_id)

            # we add the participant to the conversation
            add_participant_to_conversation(incident.conversation.channel_id, user_email)

            # we announce the participant in the conversation
            send_incident_participant_announcement_message(user_email, incident, db_session)

            # we send the welcome messages to the participant
            send_incident_welcome_participant_messages(user_email, incident, db_session)


@background_task
def incident_remove_participant_flow(user_email: str, incident_id: int, db_session=None):
    """Runs the remove participant flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if user_email == incident.commander.email:
        # we add the incident commander to the conversation again
        add_participant_to_conversation(incident.conversation.channel_id, user_email)

        # we send a notification to the channel
        send_incident_commander_readded_notification(incident)

        log.debug(
            f"Incident Commander {incident.commander.name} has been re-added to conversation {incident.conversation.channel_id}."
        )
    else:
        # we remove the participant from the incident
        participant_flows.remove_participant(user_email, incident_id, db_session)


@background_task
def incident_list_resources_flow(incident_id: int, command: Optional[dict] = None, db_session=None):
    """Runs the list incident resources flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we send the list of resources to the participant
    send_incident_resources_ephemeral_message_to_participant(
        command["user_id"], incident, db_session
    )
