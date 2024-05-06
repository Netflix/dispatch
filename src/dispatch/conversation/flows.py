import logging

from sqlalchemy.orm import Session

from dispatch.case.models import Case
from dispatch.conference.models import Conference
from dispatch.database.core import SessionLocal
from dispatch.document.models import Document
from dispatch.event import service as event_service
from dispatch.incident.models import Incident
from dispatch.plugin import service as plugin_service
from dispatch.storage.models import Storage
from dispatch.ticket.models import Ticket
from dispatch.utils import deslug_and_capitalize_resource_type
from dispatch.types import Subject

from .models import Conversation, ConversationCreate
from .service import create

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

    print(f"got convo: {conversation}")
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

    db_session.add(case)
    db_session.commit()

    return case.conversation


def create_incident_conversation(incident: Incident, db_session: SessionLocal):
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


def set_conversation_topic(incident: Incident, db_session: SessionLocal):
    """Sets the conversation topic."""
    if not incident.conversation:
        log.warning("Conversation topic not set. No conversation available for this incident.")
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Conversation topic not set. No conversation plugin enabled.")
        return

    conversation_topic = (
        f":helmet_with_white_cross: {incident.commander.individual.name}, {incident.commander.team} | "
        f"Status: {incident.status} | "
        f"Type: {incident.incident_type.name} | "
        f"Severity: {incident.incident_severity.name} | "
        f"Priority: {incident.incident_priority.name}"
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


def add_conversation_bookmark(
    db_session: Session,
    subject: Subject,
    resource: Resource,
    title: str | None = None,
):
    """Adds a conversation bookmark."""
    if not subject.conversation:
        log.warning(
            f"Conversation bookmark {resource.name.lower()} not added. No conversation available."
        )
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session,
        project_id=subject.project.id,
        plugin_type="conversation",
    )
    if not plugin:
        log.warning(
            f"Conversation bookmark {resource.name.lower()} not added. No conversation plugin enabled."
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
                f"{resource.name} bookmark not added. No {resource.name.lower()} available for subject.."
            )
        )
    except Exception as e:
        event_service.log_subject_event(
            subject=subject,
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Adding the {resource.name.lower()} bookmark failed. Reason: {e}",
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
        plugin.instance.add_to_thread(
            case.conversation.channel_id,
            case.conversation.thread_id,
            participant_emails,
        )
    except Exception as e:
        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Adding participant(s) to case conversation failed. Reason: {e}",
            case_id=case.id,
        )
        log.exception(e)


def add_incident_participants(
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


def delete_conversation(conversation: Conversation, project_id: int, db_session: SessionLocal):
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
