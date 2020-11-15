"""
.. module: dispatch.incident.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from dispatch.config import (
    DISPATCH_UI_URL,
    INCIDENT_NOTIFICATION_CONVERSATIONS,
    INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS,
)
from dispatch.conversation.enums import ConversationCommands
from dispatch.database import SessionLocal, resolve_attr
from dispatch.enums import Visibility
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import Incident, IncidentRead
from dispatch.messaging import (
    INCIDENT_CLOSED_INFORMATION_REVIEW_REMINDER_NOTIFICATION,
    INCIDENT_CLOSED_RATING_FEEDBACK_NOTIFICATION,
    INCIDENT_COMMANDER,
    INCIDENT_COMMANDER_READDED_NOTIFICATION,
    INCIDENT_NAME,
    INCIDENT_NAME_WITH_ENGAGEMENT,
    INCIDENT_NEW_ROLE_NOTIFICATION,
    INCIDENT_NOTIFICATION,
    INCIDENT_NOTIFICATION_COMMON,
    INCIDENT_PARTICIPANT_SUGGESTED_READING_ITEM,
    INCIDENT_PARTICIPANT_WELCOME_MESSAGE,
    INCIDENT_PRIORITY_CHANGE,
    INCIDENT_RESOURCES_MESSAGE,
    INCIDENT_REVIEW_DOCUMENT,
    INCIDENT_STATUS_CHANGE,
    INCIDENT_STATUS_REMINDER,
    INCIDENT_TYPE_CHANGE,
    MessageType,
)
from dispatch.document import service as document_service
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.plugin import service as plugin_service


log = logging.getLogger(__name__)


def get_suggested_documents(
    db_session, incident_type: str, priority: str, description: str
) -> list:
    """Get additional incident documents based on priority, type, and description."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="document-resolver")
    documents = []
    if plugin:
        documents = plugin.instance.get(incident_type, priority, description, db_session=db_session)
    return documents


def send_welcome_ephemeral_message_to_participant(
    participant_email: str, incident_id: int, db_session: SessionLocal
):
    """Sends an ephemeral message to the participant."""
    # we load the incident instance
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning("Incident welcome message not sent, not conversation plugin enabled.")
        return

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we send the ephemeral message
    message_kwargs = {
        "name": incident.name,
        "title": incident.title,
        "status": incident.status,
        "type": incident.incident_type.name,
        "type_description": incident.incident_type.description,
        "priority": incident.incident_priority.name,
        "priority_description": incident.incident_priority.description,
        "commander_fullname": incident.commander.name,
        "commander_weblink": incident.commander.weblink,
        "document_weblink": resolve_attr(incident, "incident_document.weblink"),
        "storage_weblink": resolve_attr(incident, "storage.weblink"),
        "ticket_weblink": resolve_attr(incident, "ticket.weblink"),
        "conference_weblink": resolve_attr(incident, "conference.weblink"),
        "conference_challenge": resolve_attr(incident, "conference.conference_challenge"),
    }

    faq_doc = document_service.get_incident_faq_document(db_session=db_session)
    if faq_doc:
        message_kwargs.update({"faq_weblink": faq_doc.weblink})

    conversation_reference = document_service.get_conversation_reference_document(
        db_session=db_session
    )
    if conversation_reference:
        message_kwargs.update(
            {"conversation_commands_reference_document_weblink": conversation_reference.weblink}
        )

    plugin.instance.send_ephemeral(
        incident.conversation.channel_id,
        participant_email,
        "Incident Welcome Message",
        INCIDENT_PARTICIPANT_WELCOME_MESSAGE,
        MessageType.incident_participant_welcome,
        **message_kwargs,
    )

    log.debug(f"Welcome ephemeral message sent to {participant_email}.")


def send_welcome_email_to_participant(
    participant_email: str, incident_id: int, db_session: SessionLocal
):
    """Sends a welcome email to the participant."""
    # we load the incident instance
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="email")
    if not plugin:
        log.warning("Participant welcome email not sent, not email plugin configured.")
        return

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    message_kwargs = {
        "name": incident.name,
        "title": incident.title,
        "status": incident.status,
        "type": incident.incident_type.name,
        "type_description": incident.incident_type.description,
        "priority": incident.incident_priority.name,
        "priority_description": incident.incident_priority.description,
        "commander_fullname": incident.commander.name,
        "commander_weblink": incident.commander.weblink,
        "document_weblink": resolve_attr(incident, "incident_document.weblink"),
        "storage_weblink": resolve_attr(incident, "storage.weblink"),
        "ticket_weblink": resolve_attr(incident, "ticket.weblink"),
        "conference_weblink": resolve_attr(incident, "conference.weblink"),
        "conference_challenge": resolve_attr(incident, "conference.conference_challenge"),
        "contact_fullname": incident.commander.name,
        "contact_weblink": incident.commander.weblink,
    }

    faq_doc = document_service.get_incident_faq_document(db_session=db_session)
    if faq_doc:
        message_kwargs.update({"faq_weblink": faq_doc.weblink})

    conversation_reference = document_service.get_conversation_reference_document(
        db_session=db_session
    )
    if conversation_reference:
        message_kwargs.update(
            {"conversation_commands_reference_document_weblink": conversation_reference.weblink}
        )

    plugin.instance.send(
        participant_email,
        INCIDENT_PARTICIPANT_WELCOME_MESSAGE,
        MessageType.incident_participant_welcome,
        **message_kwargs,
    )

    log.debug(f"Welcome email sent to {participant_email}.")


def send_incident_welcome_participant_messages(
    participant_email: str, incident_id: int, db_session: SessionLocal
):
    """Sends welcome messages to the participant."""
    # we send the welcome ephemeral message
    send_welcome_ephemeral_message_to_participant(participant_email, incident_id, db_session)

    # we send the welcome email
    send_welcome_email_to_participant(participant_email, incident_id, db_session)

    log.debug(f"Welcome participant messages sent {participant_email}.")


def get_suggested_document_items(incident_id: int, db_session: SessionLocal):
    """Create the suggested document item message."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    suggested_documents = get_suggested_documents(
        db_session, incident.incident_type, incident.incident_priority, incident.description
    )

    items = []
    if suggested_documents:
        # we send the ephemeral message
        # lets grab the first 5 documents
        # TODO add more intelligent ranking
        for i in suggested_documents[:5]:
            description = i.description
            if not description:
                if i.incident:
                    description = i.incident.title

            items.append({"name": i.name, "weblink": i.weblink, "description": description})
    return items


def send_incident_suggested_reading_messages(
    incident_id: int, items: list, participant_email: str, db_session: SessionLocal
):
    """Sends a suggested reading message to a participant."""
    if items:
        # we load the incident instance
        incident = incident_service.get(db_session=db_session, incident_id=incident_id)

        plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
        if not plugin:
            log.warning("Suggested reading message not sent, no conversation plugin enabled.")
            return

        plugin.instance.send_ephemeral(
            incident.conversation.channel_id,
            participant_email,
            "Suggested Reading",
            [INCIDENT_PARTICIPANT_SUGGESTED_READING_ITEM],
            MessageType.incident_participant_suggested_reading,
            items=items,
        )
        log.debug(f"Suggested reading ephemeral message sent to {participant_email}.")


def send_incident_status_notifications(incident: Incident, db_session: SessionLocal):
    """Sends incident status notifications to conversations and distribution lists."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification
    message_template = INCIDENT_NOTIFICATION.copy()

    # we send status notifications to conversations
    if incident.status != IncidentStatus.closed:
        message_template.insert(0, INCIDENT_NAME_WITH_ENGAGEMENT)
    else:
        message_template.insert(0, INCIDENT_NAME)

    message_kwargs = {
        "name": incident.name,
        "title": incident.title,
        "status": incident.status,
        "type": incident.incident_type.name,
        "type_description": incident.incident_type.description,
        "priority": incident.incident_priority.name,
        "priority_description": incident.incident_priority.description,
        "commander_fullname": incident.commander.name,
        "commander_weblink": incident.commander.weblink,
        "document_weblink": resolve_attr(incident, "incident_document.weblink"),
        "storage_weblink": resolve_attr(incident, "storage.weblink"),
        "ticket_weblink": resolve_attr(incident, "ticket.weblink"),
        "conference_weblink": resolve_attr(incident, "conference.weblink"),
        "conference_challenge": resolve_attr(incident, "conference.conference_challenge"),
        "contact_fullname": incident.commander.name,
        "contact_weblink": incident.commander.weblink,
        "incident_id": incident.id,
    }
    faq_doc = document_service.get_incident_faq_document(db_session=db_session)
    if faq_doc:
        message_kwargs.update({"faq_weblink": faq_doc.weblink})

    convo_plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if convo_plugin:
        for conversation in INCIDENT_NOTIFICATION_CONVERSATIONS:
            convo_plugin.instance.send(
                conversation,
                notification_text,
                message_template,
                notification_type,
                **message_kwargs,
            )
    else:
        log.warning(
            "No incident conversation notifications sent. No conversation plugin is active."
        )

    # we send status notifications to distribution lists
    email_plugin = plugin_service.get_active(db_session=db_session, plugin_type="email")
    if email_plugin:
        for distro in INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS:
            email_plugin.instance.send(
                distro, message_template, notification_type, **message_kwargs
            )
    else:
        log.warning("No incident email notifications sent. No email plugin is active.")

    log.debug("Incident status notifications sent.")


def send_incident_notifications(incident: Incident, db_session: SessionLocal):
    """Sends all incident notifications."""
    # we send the incident status notifications
    send_incident_status_notifications(incident, db_session)

    log.debug("Incident notifications sent.")


def send_incident_update_notifications(
    incident: Incident, previous_incident: IncidentRead, db_session: SessionLocal
):
    """Sends notifications about incident changes."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification
    notification_template = INCIDENT_NOTIFICATION_COMMON.copy()

    change = False
    if previous_incident.status != incident.status:
        change = True
        notification_template.append(INCIDENT_STATUS_CHANGE)

    if previous_incident.incident_type.name != incident.incident_type.name:
        change = True
        notification_template.append(INCIDENT_TYPE_CHANGE)

    if previous_incident.incident_priority.name != incident.incident_priority.name:
        change = True
        notification_template.append(INCIDENT_PRIORITY_CHANGE)

    if not change:
        # we don't need to notify
        log.debug("Incident change notifications not sent.")
        return

    notification_template.append(INCIDENT_COMMANDER)
    convo_plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")

    # we send an update to the incident conversation
    incident_conversation_notification_template = notification_template.copy()
    incident_conversation_notification_template.insert(0, INCIDENT_NAME)

    # we can't send messages to closed channels
    if incident.status != IncidentStatus.closed:
        convo_plugin.instance.send(
            incident.conversation.channel_id,
            notification_text,
            incident_conversation_notification_template,
            notification_type,
            name=incident.name,
            ticket_weblink=incident.ticket.weblink,
            title=incident.title,
            incident_type_old=previous_incident.incident_type.name,
            incident_type_new=incident.incident_type.name,
            incident_priority_old=previous_incident.incident_priority.name,
            incident_priority_new=incident.incident_priority.name,
            incident_status_old=previous_incident.status.value,
            incident_status_new=incident.status,
            commander_fullname=incident.commander.name,
            commander_weblink=incident.commander.weblink,
        )

    if incident.visibility == Visibility.open:
        notification_conversation_notification_template = notification_template.copy()
        if incident.status != IncidentStatus.closed:
            notification_conversation_notification_template.insert(0, INCIDENT_NAME_WITH_ENGAGEMENT)
        else:
            notification_conversation_notification_template.insert(0, INCIDENT_NAME)

        # we send an update to the incident notification conversations
        for conversation in INCIDENT_NOTIFICATION_CONVERSATIONS:
            convo_plugin.instance.send(
                conversation,
                notification_text,
                notification_conversation_notification_template,
                notification_type,
                name=incident.name,
                ticket_weblink=incident.ticket.weblink,
                title=incident.title,
                incident_id=incident.id,
                incident_type_old=previous_incident.incident_type.name,
                incident_type_new=incident.incident_type.name,
                incident_priority_old=previous_incident.incident_priority.name,
                incident_priority_new=incident.incident_priority.name,
                incident_status_old=previous_incident.status.value,
                incident_status_new=incident.status,
                commander_fullname=incident.commander.name,
                commander_weblink=incident.commander.weblink,
            )

        # we send an update to the incident notification distribution lists
        email_plugin = plugin_service.get_active(db_session=db_session, plugin_type="email")
        for distro in INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS:
            email_plugin.instance.send(
                distro,
                notification_template,
                notification_type,
                name=incident.name,
                title=incident.title,
                status=incident.status,
                priority=incident.incident_priority.name,
                priority_description=incident.incident_priority.description,
                commander_fullname=incident.commander.name,
                commander_weblink=incident.commander.weblink,
                document_weblink=resolve_attr(incident, "incident_document.weblink"),
                storage_weblink=resolve_attr(incident, "storage.weblink"),
                ticket_weblink=resolve_attr(incident, "ticket.weblink"),
                incident_id=incident.id,
                incident_priority_old=previous_incident.incident_priority.name,
                incident_priority_new=incident.incident_priority.name,
                incident_type_old=previous_incident.incident_type.name,
                incident_type_new=incident.incident_type.name,
                incident_status_old=previous_incident.status.value,
                incident_status_new=incident.status,
                contact_fullname=incident.commander.name,
                contact_weblink=incident.commander.weblink,
            )

    log.debug("Incident update notifications sent.")


def send_incident_participant_announcement_message(
    participant_email: str, incident_id: int, db_session=SessionLocal
):
    """Announces a participant in the conversation."""
    convo_plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not convo_plugin:
        log.warning("Incident participant annoucement not sent, no conversation plugin enabled.")
        return

    notification_text = "New Incident Participant"
    notification_type = MessageType.incident_notification
    notification_template = []

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=participant_email
    )

    participant_info = {}
    contact_plugin = plugin_service.get_active(db_session=db_session, plugin_type="contact")
    if contact_plugin:
        participant_info = contact_plugin.instance.get(participant_email)

    participant_name = participant_info.get("fullname", "Unknown")
    participant_team = participant_info.get("team", "Unknown")
    participant_department = participant_info.get("department", "Unknown")
    participant_location = participant_info.get("location", "Unknown")
    participant_weblink = participant_info.get("weblink", DISPATCH_UI_URL)

    participant_active_roles = participant_role_service.get_all_active_roles(
        db_session=db_session, participant_id=participant.id
    )
    participant_roles = []
    for role in participant_active_roles:
        participant_roles.append(role.role)

    participant_avatar_url = convo_plugin.instance.get_participant_avatar_url(participant_email)

    # TODO these shouldn't be raw blocks (kglisson)
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*{notification_text}*"}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Name:* <{participant_weblink}|{participant_name}>\n"
                    f"*Team*: {participant_team}, {participant_department}\n"
                    f"*Location*: {participant_location}\n"
                    f"*Incident Role(s)*: {(', ').join(participant_roles)}\n"
                ),
            },
            "accessory": {
                "type": "image",
                "image_url": participant_avatar_url,
                "alt_text": participant_name,
            },
        },
    ]

    convo_plugin.instance.send(
        incident.conversation.channel_id,
        notification_text,
        notification_template,
        notification_type,
        blocks=blocks,
    )

    log.debug("Incident participant announcement message sent.")


def send_incident_commander_readded_notification(incident_id: int, db_session: SessionLocal):
    """Sends a notification about re-adding the incident commander to the conversation."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning(
            "Unable to send commander re-added notification, no conversation plugin enabled."
        )
        return

    plugin.instance.send(
        incident.conversation.channel_id,
        notification_text,
        INCIDENT_COMMANDER_READDED_NOTIFICATION,
        notification_type,
        commander_fullname=incident.commander.name,
    )

    log.debug("Incident commander readded notification sent.")


def send_incident_participant_has_role_ephemeral_message(
    assigner_email: str,
    assignee_contact_info: dict,
    assignee_role: str,
    incident: Incident,
    db_session: SessionLocal,
):
    """Sends an ephemeral message to the assigner to let them know that the assignee already has the role."""
    notification_text = "Incident Assign Role Notification"

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning(
            "Unabled to send incident participant has role message, no conversation plugin enabled."
        )
        return

    plugin.instance.send_ephemeral(
        incident.conversation.channel_id,
        assigner_email,
        notification_text,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"{assignee_contact_info['fullname']} already has the {assignee_role} role.",
                },
            }
        ],
    )

    log.debug("Incident participant has role message sent.")


def send_incident_participant_role_not_assigned_ephemeral_message(
    assigner_email: str,
    assignee_contact_info: dict,
    assignee_role: str,
    incident: Incident,
    db_session: SessionLocal,
):
    """Sends an ephemeral message to the assigner to let them know that we were not able to assign the role."""
    notification_text = "Incident Assign Role Notification"

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning(
            "Unabled to send incident participant role not assigned message, no conversation plugin enabled."
        )
        return

    # TODO we should use raw blocks here (kglisson)
    plugin.instance.send_ephemeral(
        incident.conversation.channel_id,
        assigner_email,
        notification_text,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": f"We were not able to assign the {assignee_role} role to {assignee_contact_info['fullname']}.",
                },
            }
        ],
    )

    log.debug("Incident participant role not assigned message sent.")


def send_incident_new_role_assigned_notification(
    assigner_contact_info: dict,
    assignee_contact_info: dict,
    assignee_role: str,
    incident: Incident,
    db_session: SessionLocal,
):
    """Notified the conversation about the new participant role."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning("Incident new role message not sent because no conversation plugin is enabled.")
        return

    plugin.instance.send(
        incident.conversation.channel_id,
        notification_text,
        INCIDENT_NEW_ROLE_NOTIFICATION,
        notification_type,
        assigner_fullname=assigner_contact_info["fullname"],
        assigner_email=assigner_contact_info["email"],
        assignee_fullname=assignee_contact_info["fullname"],
        assignee_email=assignee_contact_info["email"],
        assignee_weblink=assignee_contact_info["weblink"],
        assignee_role=assignee_role,
    )
    log.debug("Incident new role assigned message sent.")


def send_incident_review_document_notification(
    conversation_id: str, review_document_weblink: str, db_session: SessionLocal
):
    """Sends the review document notification."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning("Incident review document not sent, no conversation enabled.")
        return

    plugin.instance.send(
        conversation_id,
        notification_text,
        [INCIDENT_REVIEW_DOCUMENT],
        notification_type,
        review_document_weblink=review_document_weblink,
    )

    log.debug("Incident review document notification sent.")


def send_incident_resources_ephemeral_message_to_participant(
    user_id: str, incident_id: int, db_session: SessionLocal
):
    """Sends the list of incident resources to the participant via an ephemeral message."""
    # we load the incident instance
    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning("Incident resource message not sent, no conversation plugin enabled.")
        return

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    message_kwargs = {
        "commander_fullname": incident.commander.name,
        "commander_weblink": incident.commander.weblink,
        "document_weblink": resolve_attr(incident, "incident_document.weblink"),
        "storage_weblink": resolve_attr(incident, "storage.weblink"),
        "ticket_weblink": resolve_attr(incident, "ticket.weblink"),
        "conference_weblink": resolve_attr(incident, "conference.weblink"),
        "conference_challenge": resolve_attr(incident, "conference.conference_challenge"),
    }

    if incident.incident_review_document:
        message_kwargs.update(
            {"review_document_weblink": incident.incident_review_document.weblink}
        )

    faq_doc = document_service.get_incident_faq_document(db_session=db_session)
    if faq_doc:
        message_kwargs.update({"faq_weblink": faq_doc.weblink})

    conversation_reference = document_service.get_conversation_reference_document(
        db_session=db_session
    )
    if conversation_reference:
        message_kwargs.update(
            {"conversation_commands_reference_document_weblink": conversation_reference.weblink}
        )

    # we send the ephemeral message
    plugin.instance.send_ephemeral(
        incident.conversation.channel_id,
        user_id,
        "Incident Resources Message",
        INCIDENT_RESOURCES_MESSAGE,
        MessageType.incident_resources_message,
        **message_kwargs,
    )

    log.debug(f"List of incident resources sent to {user_id} via ephemeral message.")


def send_incident_close_reminder(incident: Incident, db_session: SessionLocal):
    """Sends a direct message to the incident commander reminding them to close the incident if possible."""
    message_text = "Incident Status Reminder"
    message_template = INCIDENT_STATUS_REMINDER

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning("Incident close reminder message not sent, no conversation plugin enabled.")
        return

    update_command = plugin.instance.get_command_name(ConversationCommands.update_incident)

    items = [
        {
            "command": update_command,
            "name": incident.name,
            "ticket_weblink": incident.ticket.weblink,
            "title": incident.title,
            "status": incident.status,
        }
    ]

    plugin.instance.send_direct(
        incident.commander.email,
        message_text,
        message_template,
        MessageType.incident_status_reminder,
        items=items,
    )

    log.debug(f"Incident close reminder sent to {incident.commander.email}.")


def send_incident_closed_information_review_reminder(incident: Incident, db_session: SessionLocal):
    """
    Sends a direct message to the incident commander
    asking them to review the incident's information
    and to tag the incident if appropriate.
    """
    message_text = "Incident Closed Information Review Reminder"
    message_template = INCIDENT_CLOSED_INFORMATION_REVIEW_REMINDER_NOTIFICATION

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning(
            "Incident closed information review reminder message not sent, no conversation plugin enabled."
        )
        return

    items = [
        {
            "name": incident.name,
            "title": incident.title,
            "description": incident.description,
            "type": incident.incident_type.name,
            "priority": incident.incident_priority.name,
            "dispatch_ui_url": DISPATCH_UI_URL,
        }
    ]

    plugin.instance.send_direct(
        incident.commander.email,
        message_text,
        message_template,
        MessageType.incident_closed_information_review_reminder,
        items=items,
    )

    log.debug(f"Incident closed information review reminder sent to {incident.commander.email}.")


def send_incident_rating_feedback_message(incident: Incident, db_session: SessionLocal):
    """
    Sends a direct message to all incident participants asking
    them to rate and provide feedback about the incident.
    """
    notification_text = "Incident Rating and Feedback"
    notification_template = INCIDENT_CLOSED_RATING_FEEDBACK_NOTIFICATION

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    if not plugin:
        log.warning(
            "Incident rating and feedback message not sent, no conversation plugin enabled."
        )
        return

    items = [
        {
            "incident_id": incident.id,
            "name": incident.name,
            "title": incident.title,
            "ticket_weblink": incident.ticket.weblink,
        }
    ]

    for participant in incident.participants:
        plugin.instance.send_direct(
            participant.individual.email,
            notification_text,
            notification_template,
            MessageType.incident_rating_feedback,
            items=items,
        )

    log.debug("Incident rating and feedback message sent to all participants.")
