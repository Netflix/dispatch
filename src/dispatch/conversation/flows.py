import logging

from sqlalchemy.orm import Session

from dispatch.case.models import Case
from dispatch.conference.models import Conference
from dispatch.document.models import Document
from dispatch.enums import EventType
from dispatch.event import service as event_service
from dispatch.incident.models import Incident
from dispatch.messaging.strings import MessageType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack.case import messages
from dispatch.project.models import Project
from dispatch.service.models import Service
from dispatch.storage.models import Storage
from dispatch.ticket.models import Ticket
from dispatch.types import Subject
from dispatch.utils import deslug_and_capitalize_resource_type

from .models import Conversation, ConversationCreate, ConversationUpdate
from .service import create, update

log = logging.getLogger(__name__)


Resource = Document | Conference | Storage | Ticket


def create_case_conversation(
    case: Case,
    conversation_target: str,
    db_session: Session,
):
    """Create external communication conversation."""

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Conversation not created. No conversation plugin enabled.")
        return

    if not conversation_target:
        conversation_target = case.case_type.conversation_target

    conversation = None

    # Do not overwrite a case conversation with one of the same type (thread, channel)
    if case.conversation:
        if case.has_channel:
            log.warning(
                f"Trying to create case conversation but case {case.id} already has a dedicated channel conversation."
            )
            return
        if case.has_thread and not case.dedicated_channel:
            log.warning(
                "Trying to create case conversation but case {case.id} already has a thread conversation."
            )
            return

    # This case is a thread version, we send a new messaged (threaded) to the conversation target
    # for the configured case type
    if conversation_target and not case.dedicated_channel:
        try:
            conversation = plugin.instance.create_threaded(
                case=case,
                conversation_id=conversation_target,
                db_session=db_session,
            )
        except Exception as e:
            # TODO: consistency across exceptions
            log.exception(e)

    # otherwise, it must be a channel based case.
    if case.dedicated_channel:
        try:
            conversation = plugin.instance.create(
                name=f"case-{case.name}",
            )
        except Exception as e:
            # TODO: consistency across exceptions
            log.exception(e)

    if not conversation:
        log.error(f"Conversation not created. Plugin {plugin.plugin.slug} encountered an error.")
        return

    conversation.update({"resource_type": plugin.plugin.slug, "resource_id": conversation["id"]})

    if not case.conversation:
        conversation_in = ConversationCreate(
            resource_id=conversation["resource_id"],
            resource_type=conversation["resource_type"],
            weblink=conversation["weblink"],
            thread_id=conversation.get("timestamp"),
            channel_id=conversation["id"],
        )
        case.conversation = create(db_session=db_session, conversation_in=conversation_in)

        event_service.log_case_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description="Case conversation created",
            case_id=case.id,
        )
    elif case.conversation.thread_id and case.dedicated_channel:
        thread_conversation_channel_id = case.conversation.channel_id
        thread_conversation_thread_id = case.conversation.thread_id
        thread_conversation_weblink = case.conversation.weblink

        conversation_in = ConversationUpdate(
            resource_id=conversation.get("resource_id"),
            resource_type=conversation.get("resource_type"),
            weblink=conversation.get("weblink"),
            thread_id=conversation.get("timestamp"),
            channel_id=conversation.get("id"),
        )

        update(
            db_session=db_session, conversation=case.conversation, conversation_in=conversation_in
        )

        event_service.log_case_event(
            db_session=db_session,
            source=plugin.plugin.title,
            description=f"Case conversation has migrated from thread [{thread_conversation_weblink}] to channel[{case.conversation.weblink}].",
            case_id=case.id,
        )

        try:
            plugin.instance.update_thread(
                case=case,
                conversation_id=thread_conversation_channel_id,
                ts=thread_conversation_thread_id,
            )
        except Exception as e:
            event_service.log_subject_event(
                subject=case,
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Updating thread message failed. Reason: {e}",
            )
            log.exception(e)

        # Inform users in the case thread that the conversation has migrated to a channel
        try:
            plugin.instance.send(
                thread_conversation_channel_id,
                "Notify Case conversation migration",
                [],
                MessageType.case_notification,
                blocks=messages.create_case_thread_migration_message(
                    channel_weblink=conversation.get("weblink")
                ),
                ts=thread_conversation_thread_id,
            )
        except Exception as e:
            event_service.log_subject_event(
                subject=case,
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Failed to send message to original Case thread. Reason: {e}",
            )
            log.exception(e)

        # Provide users in the case channel which thread the conversation originated from.
        try:
            plugin.instance.send(
                case.conversation.channel_id,
                "Maintain Case conversation context",
                [],
                MessageType.case_notification,
                blocks=messages.create_case_channel_migration_message(
                    thread_weblink=thread_conversation_weblink
                ),
            )
        except Exception as e:
            event_service.log_subject_event(
                subject=case,
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Failed to send message to dedicated Case channel. Reason: {e}",
            )
            log.exception(e)

    db_session.add(case)
    db_session.commit()

    return case.conversation


def create_incident_conversation(incident: Incident, db_session: Session):
    """Creates a conversation."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Conversation not created. No conversation plugin enabled.")
        return

    # we create the external conversation
    try:
        external_conversation = plugin.instance.create(incident.name)
    except Exception as e:
        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Creating the incident conversation failed. Reason: {e}",
            incident_id=incident.id,
        )
        log.exception(e)
        return

    if not external_conversation:
        log.error(f"Conversation not created. Plugin {plugin.plugin.slug} encountered an error.")
        return

    external_conversation.update(
        {"resource_type": plugin.plugin.slug, "resource_id": external_conversation["id"]}
    )

    # we create the internal conversation room
    conversation_in = ConversationCreate(
        resource_id=external_conversation["resource_id"],
        resource_type=external_conversation["resource_type"],
        weblink=external_conversation["weblink"],
        channel_id=external_conversation["id"],
    )
    incident.conversation = create(conversation_in=conversation_in, db_session=db_session)

    db_session.add(incident)
    db_session.commit()

    event_service.log_incident_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Incident conversation created",
        incident_id=incident.id,
    )

    return incident.conversation


def archive_conversation(subject: Subject, db_session: Session) -> None:
    """Archives a conversation."""
    if not subject.conversation:
        log.warning("Conversation not archived. No conversation available for this subject.")
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Conversation not archived. No conversation plugin enabled.")
        return

    try:
        plugin.instance.archive(subject.conversation.channel_id)
    except Exception as e:
        event_service.log_subject_event(
            subject=subject,
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Archiving conversation failed. Reason: {e}",
        )
        log.exception(e)


def unarchive_conversation(subject: Subject, db_session: Session) -> None:
    """Unarchives a conversation."""
    if not subject.conversation:
        log.warning("Conversation not unarchived. No conversation available for this subject.")
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Conversation not unarchived. No conversation plugin enabled.")
        return

    try:
        plugin.instance.unarchive(subject.conversation.channel_id)
    except Exception as e:
        event_service.log_subject_event(
            subject=subject,
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Unarchiving conversation failed. Reason: {e}",
        )
        log.exception(e)


def get_topic_text(subject: Subject) -> str:
    """Returns the topic details based on subject"""
    if isinstance(subject, Incident):
        return (
            f":helmet_with_white_cross: {subject.commander.individual.name}, {subject.commander.team} | "
            f"Status: {subject.status} | "
            f"Type: {subject.incident_type.name} | "
            f"Severity: {subject.incident_severity.name} | "
            f"Priority: {subject.incident_priority.name}"
        )
    return (
        f":helmet_with_white_cross: {subject.assignee.individual.name}, {subject.assignee.team} | "
        f"Status: {subject.status} | "
        f"Type: {subject.case_type.name} | "
        f"Severity: {subject.case_severity.name} | "
        f"Priority: {subject.case_priority.name}"
    )


def set_conversation_topic(subject: Subject, db_session: Session) -> None:
    """Sets the conversation topic."""
    if not subject.conversation:
        log.warning("Conversation topic not set. No conversation available for this incident/case.")
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Conversation topic not set. No conversation plugin enabled.")
        return

    conversation_topic = get_topic_text(subject)

    try:
        plugin.instance.set_topic(subject.conversation.channel_id, conversation_topic)
    except Exception as e:
        event_service.log_subject_event(
            subject=subject,
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Setting the incident/case conversation topic failed. Reason: {e}",
        )
        log.exception(e)


def get_current_oncall_email(project: Project, service: Service, db_session: Session) -> str | None:
    """Notifies oncall about completed form"""
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="oncall"
    )
    if not oncall_plugin:
        log.debug("Unable to send email since oncall plugin is not active.")
    else:
        return oncall_plugin.instance.get(service.external_id)


def get_description_text(subject: Subject, db_session: Session) -> str | None:
    """Returns the description details based on the subject"""
    if not isinstance(subject, Incident):
        return

    incident_type = subject.incident_type
    if not incident_type.channel_description:
        return

    description_service = incident_type.description_service
    if description_service:
        oncall_email = get_current_oncall_email(
            project=subject.project, service=description_service, db_session=db_session
        )
        if oncall_email:
            return incident_type.channel_description.replace("{oncall_email}", oncall_email)

    return incident_type.channel_description


def set_conversation_description(subject: Subject, db_session: Session) -> None:
    """Sets the conversation description."""
    if not subject.conversation:
        log.warning("Conversation topic not set. No conversation available for this incident/case.")
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Conversation topic not set. No conversation plugin enabled.")
        return

    conversation_description = get_description_text(subject, db_session)
    if not conversation_description:
        return

    try:
        plugin.instance.set_description(subject.conversation.channel_id, conversation_description)
    except Exception as e:
        event_service.log_subject_event(
            subject=subject,
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Setting the incident/case conversation description failed. Reason: {e}",
        )
        log.exception(e)


def add_conversation_bookmark(
    db_session: Session,
    subject: Subject,
    resource: Resource,
    title: str | None = None,
):
    """Adds a conversation bookmark."""
    if not resource:
        log.warning("No conversation bookmark added since no resource available for subject.")
        return

    resource_name = (
        resource.name.lower()
        if hasattr(resource, "name")
        else (
            deslug_and_capitalize_resource_type(resource.resource_type)
            if hasattr(resource, "resource_type")
            else title
            if title
            else "untitled resource"
        )
    )

    if not subject.conversation:
        log.warning(f"Conversation bookmark {resource_name} not added. No conversation available.")
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session,
        project_id=subject.project.id,
        plugin_type="conversation",
    )
    if not plugin:
        log.warning(
            f"Conversation bookmark {resource_name} not added. No conversation plugin enabled."
        )
        return

    try:
        if not title:
            title = deslug_and_capitalize_resource_type(resource.resource_type)
        (
            plugin.instance.add_bookmark(
                subject.conversation.channel_id,
                resource.weblink,
                title=title,
            )
            if resource
            else log.warning(
                f"{resource_name} bookmark not added. No {resource_name} available for subject.."
            )
        )
    except Exception as e:
        event_service.log_subject_event(
            subject=subject,
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Adding the {resource_name} bookmark failed. Reason: {e}",
        )
        log.exception(e)


def add_case_participants(
    case: Case,
    participant_emails: list[str],
    db_session: Session,
):
    """Adds one or more participants to the case conversation."""
    if not case.conversation:
        log.warning(
            "Case participant(s) not added to conversation. No conversation available for this case."
        )
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning(
            "Case participant(s) not added to conversation. No conversation plugin enabled."
        )
        return

    try:
        if case.has_thread:
            if case.signal_instances:
                if case.signal_instances[0].signal.lifecycle == "production":
                    # we only add participants to case threads that originate from signals in production
                    plugin.instance.add_to_thread(
                        case.conversation.channel_id,
                        case.conversation.thread_id,
                        participant_emails,
                    )

                    # log event for adding participants
                    event_service.log_case_event(
                        db_session=db_session,
                        source=plugin.plugin.title,
                        description=f"{', '.join(participant_emails)} added to conversation (channel ID: {case.conversation.channel_id}, thread ID: {case.conversation.thread_id})",
                        case_id=case.id,
                        type=EventType.participant_updated,
                    )
                    log.info(f"{', '.join(participant_emails)} added to conversation (channel ID: {case.conversation.channel_id}, thread ID: {case.conversation.thread_id})")
        elif case.has_channel:
            plugin.instance.add(case.conversation.channel_id, participant_emails)

            # log event for adding participants
            event_service.log_case_event(
                db_session=db_session,
                source=plugin.plugin.title,
                description=f"{', '.join(participant_emails)} added to conversation (channel ID: {case.conversation.channel_id})",
                case_id=case.id,
                type=EventType.participant_updated,
            )
            log.info(f"{', '.join(participant_emails)} added to conversation (channel ID: {case.conversation.channel_id})")
    except Exception as e:
        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Adding participant(s) to case conversation failed. Reason: {e}",
            case_id=case.id,
        )
        log.exception(e)
        raise e


def add_incident_participants_to_conversation(
    incident: Incident,
    participant_emails: list[str],
    db_session: Session,
):
    """Adds one or more participants to the incident conversation."""
    if not incident.conversation:
        log.warning(
            "Incident participant(s) not added to conversation. No conversation available for this incident."
        )
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning(
            "Incident participant(s) not added to conversation. No conversation plugin enabled."
        )
        return

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
    else:
        log.info(
            f"Add participants {str(participant_emails)} to Incident {incident.id} successfully."
        )


def delete_conversation(conversation: Conversation, project_id: int, db_session: Session):
    """
    Renames and archives an existing conversation. Deleting a conversation
    requires admin permissions in some SaaS products.
    """
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Conversation not renamed and archived. No conversation plugin enabled.")
        return

    try:
        # we rename the conversation to avoid future naming collisions
        plugin.instance.rename(
            conversation.channel_id, f"{conversation.incident.name.lower()}-deleted"
        )
        # we archive the conversation
        plugin.instance.archive(conversation.channel_id)
    except Exception as e:
        log.exception(e)
