import logging

from datetime import datetime
from typing import Any, List

from dispatch.conference import service as conference_service
from dispatch.conference.models import ConferenceCreate
from dispatch.conversation import service as conversation_service
from dispatch.conversation.models import ConversationCreate
from dispatch.database.core import SessionLocal, resolve_attr
from dispatch.decorators import background_task
from dispatch.document import service as document_service
from dispatch.document.models import DocumentCreate
from dispatch.enums import DocumentResourceTypes
from dispatch.enums import Visibility
from dispatch.event import service as event_service
from dispatch.group import service as group_service
from dispatch.group.models import GroupCreate
from dispatch.incident import service as incident_service
from dispatch.incident.models import IncidentRead
from dispatch.incident.type import service as incident_type_service
from dispatch.individual import service as individual_service
from dispatch.messaging.strings import (
    INCIDENT_INVESTIGATION_DOCUMENT_DESCRIPTION,
    INCIDENT_INVESTIGATION_SHEET_DESCRIPTION,
)
from dispatch.participant import flows as participant_flows
from dispatch.participant import service as participant_service
from dispatch.participant.models import Participant
from dispatch.participant_role import flows as participant_role_flows
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.report.enums import ReportTypes
from dispatch.report.messaging import send_incident_report_reminder
from dispatch.service import service as service_service
from dispatch.storage import service as storage_service
from dispatch.storage.models import StorageCreate
from dispatch.task.enums import TaskStatus
from dispatch.ticket import service as ticket_service
from dispatch.ticket.models import TicketCreate

from .messaging import (
    get_suggested_document_items,
    send_incident_closed_information_review_reminder,
    send_incident_commander_readded_notification,
    send_incident_created_notifications,
    send_incident_management_help_tips_message,
    send_incident_new_role_assigned_notification,
    send_incident_open_tasks_ephemeral_message,
    send_incident_participant_announcement_message,
    send_incident_rating_feedback_message,
    send_incident_review_document_notification,
    send_incident_suggested_reading_messages,
    send_incident_update_notifications,
    send_incident_welcome_participant_messages,
)
from .models import Incident, IncidentStatus


log = logging.getLogger(__name__)


def get_incident_participants(incident: Incident, db_session: SessionLocal):
    """Get additional incident participants based on priority, type, and description."""
    individual_contacts = []
    team_contacts = []

    if incident.visibility == Visibility.open:
        plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="participant"
        )
        if plugin:
            # TODO(mvilanova): add support for resolving participants based on severity
            individual_contacts, team_contacts = plugin.instance.get(
                incident,
                db_session=db_session,
            )

            event_service.log_incident_event(
                db_session=db_session,
                source=plugin.plugin.title,
                description="Incident participants resolved",
                incident_id=incident.id,
            )

    return individual_contacts, team_contacts


def reactivate_incident_participants(incident: Incident, db_session: SessionLocal):
    """Reactivates all incident participants."""
    for participant in incident.participants:
        incident_add_or_reactivate_participant_flow(
            participant.individual.email, incident.id, db_session=db_session
        )

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident participants reactivated",
        incident_id=incident.id,
    )


def inactivate_incident_participants(incident: Incident, db_session: SessionLocal):
    """Inactivates all incident participants."""
    for participant in incident.participants:
        participant_flows.inactivate_participant(participant.individual.email, incident, db_session)

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident participants inactivated",
        incident_id=incident.id,
    )


def create_incident_ticket(incident: Incident, db_session: SessionLocal):
    """Create an external ticket for tracking."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="ticket"
    )
    if not plugin:
        log.warning("Incident ticket not created. No ticket plugin enabled.")
        return

    title = incident.title
    if incident.visibility == Visibility.restricted:
        title = incident.incident_type.name

    incident_type_plugin_metadata = incident_type_service.get_by_name_or_raise(
        db_session=db_session,
        project_id=incident.project.id,
        incident_type_in=incident.incident_type,
    ).get_meta(plugin.plugin.slug)

    ticket = plugin.instance.create(
        incident.id,
        title,
        incident.commander.individual.email,
        incident.reporter.individual.email,
        incident_type_plugin_metadata,
        db_session=db_session,
    )
    ticket.update({"resource_type": plugin.plugin.slug})

    event_service.log_incident_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Ticket created",
        incident_id=incident.id,
    )

    return ticket


def update_external_incident_ticket(
    incident_id: int,
    db_session: SessionLocal,
):
    """Update external incident ticket."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="ticket"
    )
    if not plugin:
        log.warning("External ticket not updated. No ticket plugin enabled.")
        return

    title = incident.title
    description = incident.description
    if incident.visibility == Visibility.restricted:
        title = description = incident.incident_type.name

    incident_type_plugin_metadata = incident_type_service.get_by_name_or_raise(
        db_session=db_session,
        project_id=incident.project.id,
        incident_type_in=incident.incident_type,
    ).get_meta(plugin.plugin.slug)

    total_cost = 0
    if incident.total_cost:
        total_cost = incident.total_cost

    plugin.instance.update(
        incident.ticket.resource_id,
        title,
        description,
        incident.incident_type.name,
        incident.incident_severity.name,
        incident.incident_priority.name,
        incident.status.lower(),
        incident.commander.individual.email,
        incident.reporter.individual.email,
        resolve_attr(incident, "conversation.weblink"),
        resolve_attr(incident, "incident_document.weblink"),
        resolve_attr(incident, "storage.weblink"),
        resolve_attr(incident, "conference.weblink"),
        total_cost,
        incident_type_plugin_metadata=incident_type_plugin_metadata,
    )

    event_service.log_incident_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description=f"Ticket updated. Status: {incident.status}",
        incident_id=incident.id,
    )


def create_participant_groups(
    incident: Incident,
    direct_participants: List[Any],
    indirect_participants: List[Any],
    db_session: SessionLocal,
):
    """Create external participant groups."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )

    group_name = f"{incident.name}"
    notifications_group_name = f"{group_name}-notifications"

    direct_participant_emails = [x.email for x, _ in direct_participants]
    tactical_group = plugin.instance.create(
        group_name, direct_participant_emails
    )  # add participants to core group

    indirect_participant_emails = [x.email for x in indirect_participants]
    indirect_participant_emails.append(
        tactical_group["email"]
    )  # add all those already in the tactical group
    notifications_group = plugin.instance.create(
        notifications_group_name, indirect_participant_emails
    )

    tactical_group.update(
        {
            "resource_type": f"{plugin.plugin.slug}-tactical-group",
            "resource_id": tactical_group["id"],
        }
    )
    notifications_group.update(
        {
            "resource_type": f"{plugin.plugin.slug}-notifications-group",
            "resource_id": notifications_group["id"],
        }
    )

    event_service.log_incident_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Tactical and notifications groups created",
        incident_id=incident.id,
    )

    return tactical_group, notifications_group


def create_conference(incident: Incident, participants: List[str], db_session: SessionLocal):
    """Create external conference room."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conference"
    )
    conference = plugin.instance.create(incident.name, participants=participants)

    conference.update({"resource_type": plugin.plugin.slug, "resource_id": conference["id"]})

    event_service.log_incident_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Incident conference created",
        incident_id=incident.id,
    )

    return conference


def create_incident_storage(
    incident: Incident, participant_group_emails: List[str], db_session: SessionLocal
):
    """Create an external file store for incident storage."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="storage"
    )
    storage_root_id = plugin.configuration.root_id
    storage = plugin.instance.create_file(storage_root_id, incident.name, participant_group_emails)
    storage.update({"resource_type": plugin.plugin.slug, "resource_id": storage["id"]})
    return storage


def create_incident_documents(incident: Incident, db_session: SessionLocal):
    """Create incident documents."""
    incident_documents = []

    if not incident.storage:
        return incident_documents

    # we get the storage plugin
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="storage"
    )

    if plugin:
        # we create the investigation document
        incident_document_name = f"{incident.name} - Incident Document"
        incident_document_description = INCIDENT_INVESTIGATION_DOCUMENT_DESCRIPTION

        if incident.incident_type.incident_template_document:
            incident_document_description = (
                incident.incident_type.incident_template_document.description
            )
            document = plugin.instance.copy_file(
                incident.storage.resource_id,
                incident.incident_type.incident_template_document.resource_id,
                incident_document_name,
            )
            plugin.instance.move_file(incident.storage.resource_id, document["id"])
        else:
            # we create a blank document if no template is defined
            document = plugin.instance.create_file(
                incident.storage.resource_id, incident_document_name, file_type="document"
            )

        document.update(
            {
                "name": incident_document_name,
                "description": incident_document_description,
                "resource_type": DocumentResourceTypes.incident,
                "resource_id": document["id"],
            }
        )

        incident_documents.append(document)

        event_service.log_incident_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Incident document created",
            incident_id=incident.id,
        )

        # we create the investigation sheet
        incident_sheet_name = f"{incident.name} - Incident Tracking Sheet"
        incident_sheet_description = INCIDENT_INVESTIGATION_SHEET_DESCRIPTION

        if incident.incident_type.tracking_template_document:
            incident_sheet_description = (
                incident.incident_type.tracking_template_document.description
            )
            sheet = plugin.instance.copy_file(
                incident.storage.resource_id,
                incident.incident_type.tracking_template_document.resource_id,
                incident_sheet_name,
            )
            plugin.instance.move_file(incident.storage.resource_id, sheet["id"])
        else:
            # we create a blank sheet if no template is defined
            sheet = plugin.instance.create_file(
                incident.storage.resource_id, incident_sheet_name, file_type="sheet"
            )

        sheet.update(
            {
                "name": incident_sheet_name,
                "description": incident_sheet_description,
                "resource_type": DocumentResourceTypes.tracking,
                "resource_id": sheet["id"],
            }
        )

        incident_documents.append(sheet)

        event_service.log_incident_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Incident sheet created",
            incident_id=incident.id,
        )

        # we create folders to store logs and screengrabs
        plugin.instance.create_file(incident.storage.resource_id, "logs")
        plugin.instance.create_file(incident.storage.resource_id, "screengrabs")

    return incident_documents


def create_post_incident_review_document(incident: Incident, db_session: SessionLocal):
    """Create post-incident review document."""
    # we get the storage plugin
    storage_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="storage"
    )
    if not storage_plugin:
        log.warning("Post-incident review document not created. No storage plugin enabled.")
        return

    # we create a copy of the incident review document template
    # and we move it to the incident storage
    incident_review_document_name = f"{incident.name} - Post-Incident Review Document"

    # incident review document is optional
    if not incident.incident_type.review_template_document:
        log.warning("No template for post-incident review document has been specified.")
        return

    # we create the document
    incident_review_document = storage_plugin.instance.copy_file(
        folder_id=incident.storage.resource_id,
        file_id=incident.incident_type.review_template_document.resource_id,
        name=incident_review_document_name,
    )

    incident_review_document.update(
        {
            "name": incident_review_document_name,
            "description": incident.incident_type.review_template_document.description,
            "resource_type": DocumentResourceTypes.review,
        }
    )

    # we move the document to the storage
    storage_plugin.instance.move_file(
        new_folder_id=incident.storage.resource_id,
        file_id=incident_review_document["id"],
    )

    event_service.log_incident_event(
        db_session=db_session,
        source=storage_plugin.plugin.title,
        description="Post-incident review document added to storage",
        incident_id=incident.id,
    )

    # we add the document to the incident
    document_in = DocumentCreate(
        name=incident_review_document["name"],
        description=incident_review_document["description"],
        resource_id=incident_review_document["id"],
        resource_type=incident_review_document["resource_type"],
        project=incident.project,
        weblink=incident_review_document["weblink"],
    )

    incident_review_document = document_service.create(
        db_session=db_session, document_in=document_in
    )
    incident.documents.append(incident_review_document)
    incident.incident_review_document_id = incident_review_document.id

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Post-incident review document added to incident",
        incident_id=incident.id,
    )

    # we update the post-incident review document
    update_document(incident.incident_review_document.resource_id, incident, db_session)

    db_session.add(incident)
    db_session.commit()


def update_document(document_resource_id: str, incident: Incident, db_session: SessionLocal):
    """Updates an existing document."""
    # we get the document plugin
    document_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="document"
    )

    if not document_plugin:
        log.warning("Document not updated. No document plugin enabled.")
        return

    document_plugin.instance.update(
        document_resource_id,
        commander_fullname=incident.commander.individual.name,
        conference_challenge=resolve_attr(incident, "conference.challenge"),
        conference_weblink=resolve_attr(incident, "conference.weblink"),
        conversation_weblink=resolve_attr(incident, "conversation.weblink"),
        description=incident.description,
        document_weblink=resolve_attr(incident, "incident_document.weblink"),
        name=incident.name,
        priority=incident.incident_priority.name,
        resolution=incident.resolution,
        severity=incident.incident_severity.name,
        status=incident.status,
        storage_weblink=resolve_attr(incident, "storage.weblink"),
        ticket_weblink=resolve_attr(incident, "ticket.weblink"),
        title=incident.title,
        type=incident.incident_type.name,
    )


def create_conversation(incident: Incident, db_session: SessionLocal):
    """Create external communication conversation."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )
    conversation = plugin.instance.create(incident.name)
    conversation.update({"resource_type": plugin.plugin.slug, "resource_id": conversation["name"]})

    event_service.log_incident_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Incident conversation created",
        incident_id=incident.id,
    )

    return conversation


def set_conversation_topic(incident: Incident, db_session: SessionLocal):
    """Sets the conversation topic."""
    if not incident.conversation:
        log.warning("Conversation topic not set. No conversation available for this incident.")
        return

    conversation_topic = (
        f":helmet_with_white_cross: {incident.commander.individual.name}, {incident.commander.team} - "
        f"Type: {incident.incident_type.name} - "
        f"Severity: {incident.incident_severity.name} - "
        f"Priority: {incident.incident_priority.name} - "
        f"Status: {incident.status}"
    )

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )

    try:
        plugin.instance.set_topic(incident.conversation.channel_id, conversation_topic)
    except Exception as e:
        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Setting the incident conversation topic failed. Reason: {e}",
            incident_id=incident.id,
        )
        log.exception(e)


def add_participants_to_conversation(
    participant_emails: List[str], incident: Incident, db_session: SessionLocal
):
    """Adds one or more participants to the conversation."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )

    if plugin:
        try:
            plugin.instance.add(incident.conversation.channel_id, participant_emails)
        except Exception as e:
            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Adding participant(s) to incident conversation failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)


def add_participant_to_tactical_group(
    user_email: str, incident: Incident, db_session: SessionLocal
):
    """Adds participant to the tactical group."""
    # we get the tactical group
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )
    if plugin:
        tactical_group = group_service.get_by_incident_id_and_resource_type(
            db_session=db_session,
            incident_id=incident.id,
            resource_type=f"{plugin.plugin.slug}-tactical-group",
        )
        if tactical_group:
            plugin.instance.add(tactical_group.email, [user_email])


def remove_participant_from_tactical_group(
    user_email: str, incident: Incident, db_session: SessionLocal
):
    """Removes participant from the tactical group."""
    # we get the tactical group
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )
    if plugin:
        tactical_group = group_service.get_by_incident_id_and_resource_type(
            db_session=db_session,
            incident_id=incident.id,
            resource_type=f"{plugin.plugin.slug}-tactical-group",
        )
        if tactical_group:
            plugin.instance.remove(tactical_group.email, [user_email])


@background_task
def incident_create_stable_flow(
    *, incident_id: int, organization_slug: str = None, db_session=None
):
    """Creates all resources necessary when an incident is created as 'stable'."""
    incident_create_flow(
        incident_id=incident_id, organization_slug=organization_slug, db_session=db_session
    )
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    incident_stable_status_flow(incident=incident, db_session=db_session)


@background_task
def incident_create_closed_flow(
    *, incident_id: int, organization_slug: str = None, db_session=None
):
    """Creates all resources necessary when an incident is created as 'closed'."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we inactivate all participants
    inactivate_incident_participants(incident, db_session)

    # we set the stable and close times to the reported time
    incident.stable_at = incident.closed_at = incident.reported_at

    ticket = create_incident_ticket(incident, db_session)
    if ticket:
        incident.ticket = ticket_service.create(
            db_session=db_session, ticket_in=TicketCreate(**ticket)
        )

        incident.name = ticket["resource_id"]
        update_external_incident_ticket(incident.id, db_session)

    db_session.add(incident)
    db_session.commit()


@background_task
def incident_create_flow(*, organization_slug: str, incident_id: int, db_session=None):
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

    individual_participants, team_participants = get_incident_participants(incident, db_session)

    tactical_group = notifications_group = None
    group_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )
    if group_plugin:
        try:
            tactical_group_external, notifications_group_external = create_participant_groups(
                incident, individual_participants, team_participants, db_session
            )

            if tactical_group_external and notifications_group_external:
                tactical_group_in = GroupCreate(
                    name=tactical_group_external["name"],
                    email=tactical_group_external["email"],
                    resource_type=tactical_group_external["resource_type"],
                    resource_id=tactical_group_external["resource_id"],
                    weblink=tactical_group_external["weblink"],
                )
                tactical_group = group_service.create(
                    db_session=db_session, group_in=tactical_group_in
                )
                incident.groups.append(tactical_group)
                incident.tactical_group_id = tactical_group.id

                notifications_group_in = GroupCreate(
                    name=notifications_group_external["name"],
                    email=notifications_group_external["email"],
                    resource_type=notifications_group_external["resource_type"],
                    resource_id=notifications_group_external["resource_id"],
                    weblink=notifications_group_external["weblink"],
                )
                notifications_group = group_service.create(
                    db_session=db_session, group_in=notifications_group_in
                )
                incident.groups.append(notifications_group)
                incident.notifications_group_id = notifications_group.id

                event_service.log_incident_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description="Tactical and notifications groups added to incident",
                    incident_id=incident.id,
                )
        except Exception as e:
            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of tactical and notifications groups failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

    storage_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="storage"
    )
    if storage_plugin:
        # we create the storage resource
        try:
            if group_plugin:
                group_emails = []
                if tactical_group and notifications_group:
                    group_emails = [tactical_group.email, notifications_group.email]

                storage = create_incident_storage(incident, group_emails, db_session)
            else:
                participant_emails = [x.email for x, _ in individual_participants]

                # we don't have a group so add participants directly
                storage = create_incident_storage(incident, participant_emails, db_session)

            storage_in = StorageCreate(
                resource_id=storage["resource_id"],
                resource_type=storage["resource_type"],
                weblink=storage["weblink"],
            )

            incident.storage = storage_service.create(
                db_session=db_session,
                storage_in=storage_in,
            )

            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description="Storage added to incident",
                incident_id=incident.id,
            )
        except Exception as e:
            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of incident storage failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

        # we create collaboration documents, don't fail the whole flow if this fails
        try:
            incident_documents = create_incident_documents(incident, db_session)

            for d in incident_documents:
                document_in = DocumentCreate(
                    name=d["name"],
                    description=d["description"],
                    resource_id=d["resource_id"],
                    project={"name": incident.project.name},
                    resource_type=d["resource_type"],
                    weblink=d["weblink"],
                )
                document = document_service.create(db_session=db_session, document_in=document_in)
                incident.documents.append(document)

                if document.resource_type == DocumentResourceTypes.incident:
                    incident.incident_document_id = document.id

            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description="Collaboration documents added to incident",
                incident_id=incident.id,
            )
        except Exception as e:
            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of collaboration documents failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

    conference_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conference"
    )
    if conference_plugin:
        try:
            participant_emails = [x.email for x, _ in individual_participants]

            if group_plugin and tactical_group:
                # we use the tactical group email if the group plugin is enabled
                participant_emails = [tactical_group.email]

            conference = create_conference(incident, participant_emails, db_session)

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

            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description="Conference added to incident",
                incident_id=incident.id,
            )
        except Exception as e:
            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of incident conference failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

    # we create the conversation for real-time communications

    conversation_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )
    if conversation_plugin:
        try:
            conversation = create_conversation(incident, db_session)

            conversation_in = ConversationCreate(
                resource_id=conversation["resource_id"],
                resource_type=conversation["resource_type"],
                weblink=conversation["weblink"],
                channel_id=conversation["id"],
            )
            incident.conversation = conversation_service.create(
                db_session=db_session, conversation_in=conversation_in
            )

            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description="Conversation added to incident",
                incident_id=incident.id,
            )

            # we set the conversation topic
            set_conversation_topic(incident, db_session)
        except Exception as e:
            event_service.log_incident_event(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Creation of incident conversation failed. Reason: {e}",
                incident_id=incident.id,
            )
            log.exception(e)

    # we update the incident ticket
    update_external_incident_ticket(incident.id, db_session)

    # we update the investigation document
    document_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="document"
    )
    if document_plugin:
        if incident.incident_document:
            try:
                document_plugin.instance.update(
                    incident.incident_document.resource_id,
                    commander_fullname=incident.commander.individual.name,
                    conference_challenge=resolve_attr(incident, "conference.challenge"),
                    conference_weblink=resolve_attr(incident, "conference.weblink"),
                    conversation_weblink=resolve_attr(incident, "conversation.weblink"),
                    description=incident.description,
                    document_weblink=resolve_attr(incident, "incident_document.weblink"),
                    name=incident.name,
                    priority=incident.incident_priority.name,
                    severity=incident.incident_severity.name,
                    status=incident.status,
                    storage_weblink=resolve_attr(incident, "storage.weblink"),
                    ticket_weblink=resolve_attr(incident, "ticket.weblink"),
                    title=incident.title,
                    type=incident.incident_type.name,
                )
            except Exception as e:
                event_service.log_incident_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description=f"Incident documents rendering failed. Reason: {e}",
                    incident_id=incident.id,
                )
                log.exception(e)

    # we defer this setup for all resolved incident roles until after resources have been created
    roles = ["reporter", "commander", "liaison", "scribe"]

    user_emails = [
        resolve_attr(incident, f"{role}.individual.email")
        for role in roles
        if resolve_attr(incident, role)
    ]
    user_emails = list(dict.fromkeys(user_emails))

    for user_email in user_emails:
        # we add the participant to the tactical group
        add_participant_to_tactical_group(user_email, incident, db_session)

        # we add the participant to the conversation
        add_participants_to_conversation([user_email], incident, db_session)

        # we announce the participant in the conversation
        send_incident_participant_announcement_message(user_email, incident, db_session)

        # we send the welcome messages to the participant
        send_incident_welcome_participant_messages(user_email, incident, db_session)

        # we send a suggested reading message to the participant
        suggested_document_items = get_suggested_document_items(incident, db_session)
        send_incident_suggested_reading_messages(
            incident, suggested_document_items, user_email, db_session
        )

    # wait until all resources are created before adding suggested participants
    for individual, service_id in individual_participants:
        incident_add_or_reactivate_participant_flow(
            individual.email,
            incident.id,
            participant_role=ParticipantRoleType.observer,
            service_id=service_id,
            db_session=db_session,
        )

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident participants added to incident",
        incident_id=incident.id,
    )

    send_incident_created_notifications(incident, db_session)

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident notifications sent",
        incident_id=incident.id,
    )

    # we page the incident commander based on incident priority
    if incident.incident_priority.page_commander:
        if incident.commander.service:
            service_id = incident.commander.service.external_id
            oncall_plugin = plugin_service.get_active_instance(
                db_session=db_session, project_id=incident.project.id, plugin_type="oncall"
            )
            if oncall_plugin:
                oncall_plugin.instance.page(
                    service_id=service_id,
                    incident_name=incident.name,
                    incident_title=incident.title,
                    incident_description=incident.description,
                )
            else:
                log.warning("Incident commander not paged. No plugin of type oncall enabled.")
        else:
            log.warning(
                "Incident commander not paged. No relationship between commander and an oncall service."
            )

    # we send a message to the incident commander with tips on how to manage the incident
    send_incident_management_help_tips_message(incident, db_session)

    db_session.add(incident)
    db_session.commit()
    return incident


def incident_active_status_flow(incident: Incident, db_session=None):
    """Runs the incident active flow."""
    # we un-archive the conversation
    convo_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )
    if convo_plugin:
        convo_plugin.instance.unarchive(incident.conversation.channel_id)


def incident_stable_status_flow(incident: Incident, db_session=None):
    """Runs the incident stable flow."""
    # we set the stable time
    incident.stable_at = datetime.utcnow()
    db_session.add(incident)
    db_session.commit()

    if incident.incident_document:
        # we update the incident document
        update_document(incident.incident_document.resource_id, incident, db_session)

    if incident.incident_review_document:
        log.debug(
            "The post-incident review document has already been created. Skipping creation..."
        )
        return

    # we create the post-incident review document
    create_post_incident_review_document(incident, db_session)

    if incident.incident_review_document:
        # we send a notification about the incident review document to the conversation
        send_incident_review_document_notification(
            incident.conversation.channel_id,
            incident.incident_review_document.weblink,
            incident,
            db_session,
        )


def incident_closed_status_flow(incident: Incident, db_session=None):
    """Runs the incident closed flow."""
    # we inactivate all participants
    inactivate_incident_participants(incident, db_session)

    # we set the closed time
    incident.closed_at = datetime.utcnow()
    db_session.add(incident)
    db_session.commit()

    # we archive the conversation
    convo_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )
    if convo_plugin:
        convo_plugin.instance.archive(incident.conversation.channel_id)

    # storage for incidents with restricted visibility is never opened
    if incident.visibility == Visibility.open:
        # add organization wide permission
        storage_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="storage"
        )
        if storage_plugin:
            if storage_plugin.configuration.open_on_close:
                # typically only broad access to the incident document itself is required.
                storage_plugin.instance.open(incident.incident_document.resource_id)

                event_service.log_incident_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description="Incident document opened to anyone in the domain",
                    incident_id=incident.id,
                )

            if storage_plugin.configuration.read_only:
                # unfortunately this can't be applied at the folder level
                # so we just mark the incident doc as available.
                storage_plugin.instance.mark_readonly(incident.incident_document.resource_id)

                event_service.log_incident_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description="Incident document marked as readonly",
                    incident_id=incident.id,
                )

    # we send a direct message to the incident commander asking to review
    # the incident's information and to tag the incident if appropiate
    send_incident_closed_information_review_reminder(incident, db_session)

    # we send a direct message to all participants asking them
    # to rate and provide feedback about the incident
    send_incident_rating_feedback_message(incident, db_session)


def conversation_topic_dispatcher(
    user_email: str,
    incident: Incident,
    previous_incident: dict,
    db_session: SessionLocal,
):
    """Determines if the conversation topic needs to be updated."""
    # we load the individual
    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=user_email, project_id=incident.project.id
    )

    conversation_topic_change = False
    if previous_incident.title != incident.title:
        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f'{individual.name} changed the incident title to "{incident.title}"',
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.description != incident.description:
        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident description",
            details={"description": incident.description},
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.incident_type.name != incident.incident_type.name:
        conversation_topic_change = True

        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident type to {incident.incident_type.name}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.incident_severity.name != incident.incident_severity.name:
        conversation_topic_change = True

        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident severity to {incident.incident_severity.name}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.incident_priority.name != incident.incident_priority.name:
        conversation_topic_change = True

        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} changed the incident priority to {incident.incident_priority.name}",
            incident_id=incident.id,
            individual_id=individual.id,
        )

    if previous_incident.status != incident.status:
        conversation_topic_change = True

        event_service.log_incident_event(
            db_session=db_session,
            source="Incident Participant",
            description=f"{individual.name} marked the incident as {incident.status.lower()}",
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
        if previous_status == IncidentStatus.closed:
            # re-activate incident
            incident_active_status_flow(incident=incident, db_session=db_session)
            reactivate_incident_participants(incident=incident, db_session=db_session)
            send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)
        elif previous_status == IncidentStatus.stable:
            send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)

    # we currently have a stable incident
    elif current_status == IncidentStatus.stable:
        if previous_status == IncidentStatus.active:
            incident_stable_status_flow(incident=incident, db_session=db_session)
            send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)
        elif previous_status == IncidentStatus.closed:
            incident_active_status_flow(incident=incident, db_session=db_session)
            incident_stable_status_flow(incident=incident, db_session=db_session)
            reactivate_incident_participants(incident=incident, db_session=db_session)
            send_incident_report_reminder(incident, ReportTypes.tactical_report, db_session)

    # we currently have a closed incident
    elif current_status == IncidentStatus.closed:
        if previous_status == IncidentStatus.active:
            incident_stable_status_flow(incident=incident, db_session=db_session)
            incident_closed_status_flow(incident=incident, db_session=db_session)
        elif previous_status == IncidentStatus.stable:
            incident_closed_status_flow(incident=incident, db_session=db_session)

    if previous_status != current_status:
        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"The incident status has been changed from {previous_status.lower()} to {current_status.lower()}",  # noqa
            incident_id=incident.id,
        )


@background_task
def incident_update_flow(
    user_email: str,
    commander_email: str,
    reporter_email: str,
    incident_id: int,
    previous_incident: IncidentRead,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the incident update flow."""
    # we load the incident
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if incident.commander.individual.email != commander_email:
        # we assign the commander role to another participant
        incident_assign_role_flow(
            incident_id=incident_id,
            assigner_email=user_email,
            assignee_email=commander_email,
            assignee_role=ParticipantRoleType.incident_commander,
            db_session=db_session,
        )

    if incident.reporter.individual.email != reporter_email:
        # we assign the reporter role to another participant
        incident_assign_role_flow(
            incident_id=incident_id,
            assigner_email=user_email,
            assignee_email=reporter_email,
            assignee_role=ParticipantRoleType.reporter,
            db_session=db_session,
        )

    # we run the active, stable or closed flows based on incident status change
    status_flow_dispatcher(
        incident, incident.status, previous_incident.status, db_session=db_session
    )

    # we update the conversation topic
    conversation_topic_dispatcher(user_email, incident, previous_incident, db_session=db_session)

    # we update the external ticket
    update_external_incident_ticket(incident_id, db_session)

    if incident.status == IncidentStatus.active:
        # we re-resolve and add individuals to the incident
        individual_participants, team_participants = get_incident_participants(incident, db_session)

        for individual, service_id in individual_participants:
            incident_add_or_reactivate_participant_flow(
                individual.email,
                incident.id,
                participant_role=ParticipantRoleType.observer,
                service_id=service_id,
                db_session=db_session,
            )

        # we add the team distributions lists to the notifications group
        # we only have to do this for teams as new members
        # will be added to the tactical group on incident join
        group_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
        )
        if group_plugin:
            team_participant_emails = [x.email for x in team_participants]
            group_plugin.instance.add(incident.notifications_group.email, team_participant_emails)

    # we send the incident update notifications
    send_incident_update_notifications(incident, previous_incident, db_session)


def incident_assign_role_flow(
    incident_id: int,
    assigner_email: str,
    assignee_email: str,
    assignee_role: str,
    db_session: SessionLocal,
):
    """Runs the incident participant role assignment flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we add the assignee to the incident if they're not a participant
    incident_add_or_reactivate_participant_flow(assignee_email, incident.id, db_session=db_session)

    # we run the participant assign role flow
    result = participant_role_flows.assign_role_flow(
        incident, assignee_email, assignee_role, db_session
    )

    if result == "assignee_has_role":
        # NOTE: This is disabled until we can determine the source of the caller
        # we let the assigner know that the assignee already has this role
        # send_incident_participant_has_role_ephemeral_message(
        # 	assigner_email, assignee_contact_info, assignee_role, incident
        # )
        return

    if result == "role_not_assigned":
        # NOTE: This is disabled until we can determine the source of the caller
        # we let the assigner know that we were not able to assign the role
        # send_incident_participant_role_not_assigned_ephemeral_message(
        # 	assigner_email, assignee_contact_info, assignee_role, incident
        # )
        return

    if incident.status != IncidentStatus.closed:
        if assignee_role != ParticipantRoleType.participant:
            # we resolve the assigner and assignee contact information
            contact_plugin = plugin_service.get_active_instance(
                db_session=db_session, project_id=incident.project.id, plugin_type="contact"
            )

            if contact_plugin:
                assigner_contact_info = contact_plugin.instance.get(
                    assigner_email, db_session=db_session
                )
                assignee_contact_info = contact_plugin.instance.get(
                    assignee_email, db_session=db_session
                )
            else:
                assigner_contact_info = {
                    "email": assigner_email,
                    "fullname": "Unknown",
                    "weblink": "",
                }
                assignee_contact_info = {
                    "email": assignee_email,
                    "fullname": "Unknown",
                    "weblink": "",
                }

            # we send a notification to the incident conversation
            send_incident_new_role_assigned_notification(
                assigner_contact_info, assignee_contact_info, assignee_role, incident, db_session
            )

        if assignee_role == ParticipantRoleType.incident_commander:
            # we update the conversation topic
            set_conversation_topic(incident, db_session)

            # we send a message to the incident commander with tips on how to manage the incident
            send_incident_management_help_tips_message(incident, db_session)


@background_task
def incident_engage_oncall_flow(
    user_email: str,
    incident_id: int,
    oncall_service_external_id: str,
    page=None,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the incident engage oncall flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we resolve the oncall service
    oncall_service = service_service.get_by_external_id_and_project_id(
        db_session=db_session,
        external_id=oncall_service_external_id,
        project_id=incident.project.id,
    )

    # we get the active oncall plugin
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="oncall"
    )

    if oncall_plugin:
        if oncall_plugin.plugin.slug != oncall_service.type:
            log.warning(
                f"Unable to engage the oncall. Oncall plugin enabled not of type {oncall_plugin.plugin.slug}."  # noqa
            )
            return None, None
    else:
        log.warning("Unable to engage the oncall. No oncall plugins enabled.")
        return None, None

    oncall_email = oncall_plugin.instance.get(service_id=oncall_service_external_id)

    # we attempt to add the oncall to the incident
    oncall_participant_added = incident_add_or_reactivate_participant_flow(
        oncall_email, incident.id, service_id=oncall_service.id, db_session=db_session
    )

    if not oncall_participant_added:
        # we already have the oncall for the service in the incident
        return None, oncall_service

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=user_email, project_id=incident.project.id
    )

    event_service.log_incident_event(
        db_session=db_session,
        source=oncall_plugin.plugin.title,
        description=f"{individual.name} engages oncall service {oncall_service.name}",
        incident_id=incident.id,
    )

    if page == "Yes":
        # we page the oncall
        oncall_plugin.instance.page(
            service_id=oncall_service_external_id,
            incident_name=incident.name,
            incident_title=incident.title,
            incident_description=incident.description,
        )

        event_service.log_incident_event(
            db_session=db_session,
            source=oncall_plugin.plugin.title,
            description=f"{oncall_service.name} on-call paged",
            incident_id=incident.id,
        )

    return oncall_participant_added.individual, oncall_service


@background_task
def incident_add_participant_to_tactical_group_flow(
    user_email: str,
    incident_id: Incident,
    organization_slug: str,
    db_session: SessionLocal,
):
    """Adds participant to the tactical group."""
    # we get the tactical group
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    add_participant_to_tactical_group(
        db_session=db_session, incident=incident, user_email=user_email
    )


@background_task
def incident_add_or_reactivate_participant_flow(
    user_email: str,
    incident_id: int,
    participant_role: ParticipantRoleType = ParticipantRoleType.participant,
    service_id: int = 0,
    event: dict = None,
    organization_slug: str = None,
    db_session=None,
) -> Participant:
    """Runs the incident add or reactivate participant flow."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if service_id:
        # we need to ensure that we don't add another member of a service if one
        # already exists (e.g. overlapping oncalls, we assume they will hand-off if necessary)
        participant = participant_service.get_by_incident_id_and_service_id(
            incident_id=incident_id, service_id=service_id, db_session=db_session
        )

        if participant:
            log.debug("Skipping resolved participant. Oncall service member already engaged.")
            return

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=user_email
    )

    if participant:
        if participant.active_roles:
            return participant

        if incident.status != IncidentStatus.closed:
            # we reactivate the participant
            participant_flows.reactivate_participant(
                user_email, incident, db_session, service_id=service_id
            )
    else:
        # we add the participant to the incident
        participant = participant_flows.add_participant(
            user_email, incident, db_session, service_id=service_id, role=participant_role
        )

    # we add the participant to the tactical group
    add_participant_to_tactical_group(user_email, incident, db_session)

    if incident.status != IncidentStatus.closed:
        # we add the participant to the conversation
        add_participants_to_conversation([user_email], incident, db_session)

        # we announce the participant in the conversation
        send_incident_participant_announcement_message(user_email, incident, db_session)

        # we send the welcome messages to the participant
        send_incident_welcome_participant_messages(user_email, incident, db_session)

        # we send a suggested reading message to the participant
        suggested_document_items = get_suggested_document_items(incident, db_session)
        send_incident_suggested_reading_messages(
            incident, suggested_document_items, user_email, db_session
        )

    return participant


@background_task
def incident_remove_participant_flow(
    user_email: str,
    incident_id: int,
    event: dict = None,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the remove participant flow."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=user_email
    )

    for task in incident.tasks:
        if task.status == TaskStatus.open:
            for assignee in task.assignees:
                if assignee == participant:
                    # we add the participant back to the conversation
                    add_participants_to_conversation([user_email], incident, db_session)

                    # we ask the participant to resolve or re-assign
                    # their tasks before leaving the incident conversation
                    send_incident_open_tasks_ephemeral_message(user_email, incident, db_session)

                    return

    if user_email == incident.commander.individual.email:
        # we add the incident commander back to the conversation
        add_participants_to_conversation([user_email], incident, db_session)

        # we send a notification to the channel
        send_incident_commander_readded_notification(incident, db_session)

        return

    # we remove the participant from the incident
    participant_flows.remove_participant(user_email, incident, db_session)

    # we remove the participant to the tactical group
    remove_participant_from_tactical_group(user_email, incident, db_session)
