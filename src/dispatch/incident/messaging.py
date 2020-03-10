"""
.. module: dispatch.incident.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from dispatch.config import (
    INCIDENT_PLUGIN_CONTACT_SLUG,
    INCIDENT_PLUGIN_CONVERSATION_SLUG,
    INCIDENT_RESOURCE_FAQ_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    INCIDENT_PLUGIN_EMAIL_SLUG,
    INCIDENT_NOTIFICATION_CONVERSATIONS,
    INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS,
)
from dispatch.database import SessionLocal
from dispatch.messaging import (
    INCIDENT_COMMANDER_READDED_NOTIFICATION,
    INCIDENT_NEW_ROLE_NOTIFICATION,
    INCIDENT_NOTIFICATION,
    INCIDENT_NOTIFICATION_PRIORITY_CHANGE,
    INCIDENT_NOTIFICATION_TYPE_AND_PRIORITY_CHANGE,
    INCIDENT_NOTIFICATION_TYPE_CHANGE,
    INCIDENT_PARTICIPANT_WELCOME_MESSAGE,
    INCIDENT_RESOURCES_MESSAGE,
    INCIDENT_REVIEW_DOCUMENT_NOTIFICATION,
    MessageType,
)
from dispatch.document.service import get_by_incident_id_and_resource_type as get_document
from dispatch.incident import service as incident_service
from dispatch.incident.models import Incident
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.plugins.base import plugins


log = logging.getLogger(__name__)


def send_welcome_ephemeral_message_to_participant(
    participant_email: str, incident_id: int, db_session: SessionLocal
):
    """Sends an ephemeral message to the participant."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we get the incident documents
    incident_document = get_document(
        db_session=db_session,
        incident_id=incident_id,
        resource_type=INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    )

    incident_faq = get_document(
        db_session=db_session, incident_id=incident_id, resource_type=INCIDENT_RESOURCE_FAQ_DOCUMENT
    )

    # we send the ephemeral message
    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send_ephemeral(
        incident.conversation.channel_id,
        participant_email,
        "Incident Welcome Message",
        INCIDENT_PARTICIPANT_WELCOME_MESSAGE,
        MessageType.incident_participant_welcome,
        name=incident.name,
        title=incident.title,
        status=incident.status,
        priority=incident.incident_priority.name,
        commander_fullname=incident.commander.name,
        commander_weblink=incident.commander.weblink,
        document_weblink=incident_document.weblink,
        storage_weblink=incident.storage.weblink,
        ticket_weblink=incident.ticket.weblink,
        faq_weblink=incident_faq.weblink,
    )

    log.debug(f"Welcome ephemeral message sent to {participant_email}.")


def send_welcome_email_to_participant(
    participant_email: str, incident_id: int, db_session: SessionLocal
):
    """Sends a welcome email to the participant."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we get the incident documents
    incident_document = get_document(
        db_session=db_session,
        incident_id=incident_id,
        resource_type=INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    )

    incident_faq = get_document(
        db_session=db_session, incident_id=incident_id, resource_type=INCIDENT_RESOURCE_FAQ_DOCUMENT
    )

    email_plugin = plugins.get(INCIDENT_PLUGIN_EMAIL_SLUG)
    email_plugin.send(
        participant_email,
        INCIDENT_PARTICIPANT_WELCOME_MESSAGE,
        MessageType.incident_participant_welcome,
        name=incident.name,
        title=incident.title,
        status=incident.status,
        priority=incident.incident_priority.name,
        commander_fullname=incident.commander.name,
        commander_weblink=incident.commander.weblink,
        document_weblink=incident_document.weblink,
        storage_weblink=incident.storage.weblink,
        ticket_weblink=incident.ticket.weblink,
        faq_weblink=incident_faq.weblink,
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


def send_incident_status_notifications(incident: Incident, db_session: SessionLocal):
    """Sends incident status notifications to conversations and distribution lists."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification
    message_template = INCIDENT_NOTIFICATION

    # we get the incident documents
    incident_document = get_document(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    )

    incident_faq = get_document(
        db_session=db_session, incident_id=incident.id, resource_type=INCIDENT_RESOURCE_FAQ_DOCUMENT
    )

    # we send status notifications to conversations
    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    for conversation in INCIDENT_NOTIFICATION_CONVERSATIONS:
        convo_plugin.send(
            conversation,
            notification_text,
            message_template,
            notification_type,
            name=incident.name,
            title=incident.title,
            status=incident.status,
            priority=incident.incident_priority.name,
            commander_fullname=incident.commander.name,
            commander_weblink=incident.commander.weblink,
            document_weblink=incident_document.weblink,
            storage_weblink=incident.storage.weblink,
            ticket_weblink=incident.ticket.weblink,
            faq_weblink=incident_faq.weblink,
            incident_id=incident.id,
        )

    # we send status notifications to distribution lists
    email_plugin = plugins.get(INCIDENT_PLUGIN_EMAIL_SLUG)
    for distro in INCIDENT_NOTIFICATION_DISTRIBUTION_LISTS:
        email_plugin.send(
            distro,
            message_template,
            notification_type,
            name=incident.name,
            title=incident.title,
            status=incident.status,
            priority=incident.incident_priority.name,
            commander_fullname=incident.commander.name,
            commander_weblink=incident.commander.weblink,
            document_weblink=incident_document.weblink,
            storage_weblink=incident.storage.weblink,
            ticket_weblink=incident.ticket.weblink,
            faq_weblink=incident_faq.weblink,
            incident_id=incident.id,
        )

    log.debug(f"Incident status notifications sent.")


def send_incident_notifications(incident: Incident, db_session: SessionLocal):
    """Sends all incident notifications."""
    # we send the incident status notifications
    send_incident_status_notifications(incident, db_session)

    log.debug(f"Incident notifications sent.")


def send_incident_change_notifications(
    incident: Incident, incident_title: str, incident_type: str, incident_priority: str
):
    """Sends notifications about incident changes."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification
    notification_template = []

    if (
        incident_type != incident.incident_type.name
        and incident_priority != incident.incident_priority.name
    ):
        notification_template = INCIDENT_NOTIFICATION_TYPE_AND_PRIORITY_CHANGE
    elif (
        incident_type != incident.incident_type.name
        and incident_priority == incident.incident_priority.name
    ):
        notification_template = INCIDENT_NOTIFICATION_TYPE_CHANGE
    elif (
        incident_type == incident.incident_type.name
        and incident_priority != incident.incident_priority.name
    ):
        notification_template = INCIDENT_NOTIFICATION_PRIORITY_CHANGE
    else:
        # we don't need to notify
        log.debug(f"Incident change notifications not sent.")
        return

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)

    # we notify the incident conversation
    convo_plugin.send(
        incident.conversation.channel_id,
        notification_text,
        notification_template,
        notification_type,
        name=incident.name,
        ticket_weblink=incident.ticket.weblink,
        title=incident_title,
        incident_type_old=incident.incident_type.name,
        incident_type_new=incident_type,
        incident_priority_old=incident.incident_priority.name,
        incident_priority_new=incident_priority,
        commander_fullname=incident.commander.name,
        commander_weblink=incident.commander.weblink,
    )

    # we notify the notification conversations
    for conversation in INCIDENT_NOTIFICATION_CONVERSATIONS:
        convo_plugin.send(
            conversation,
            notification_text,
            notification_template,
            notification_type,
            name=incident.name,
            ticket_weblink=incident.ticket.weblink,
            title=incident_title,
            incident_type_old=incident.incident_type.name,
            incident_type_new=incident_type,
            incident_priority_old=incident.incident_priority.name,
            incident_priority_new=incident_priority,
            commander_fullname=incident.commander.name,
            commander_weblink=incident.commander.weblink,
        )

    log.debug(f"Incident change notifications sent.")


def send_incident_participant_announcement_message(
    participant_email: str, incident_id: int, db_session=SessionLocal
):
    """Announces a participant in the conversation."""
    notification_text = "New Incident Participant"
    notification_type = MessageType.incident_notification
    notification_template = []

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=participant_email
    )

    contact_plugin = plugins.get(INCIDENT_PLUGIN_CONTACT_SLUG)
    participant_info = contact_plugin.get(participant_email)

    participant_name = participant_info["fullname"]
    participant_team = participant_info["team"]
    participant_department = participant_info["department"]
    participant_location = participant_info["location"]
    participant_weblink = participant_info["weblink"]

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    participant_avatar_url = convo_plugin.get_participant_avatar_url(participant_email)

    participant_active_roles = participant_role_service.get_all_active_roles(
        db_session=db_session, participant_id=participant.id
    )
    participant_roles = []
    for role in participant_active_roles:
        participant_roles.append(role.role)

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

    convo_plugin.send(
        incident.conversation.channel_id,
        notification_text,
        notification_template,
        notification_type,
        blocks=blocks,
    )

    log.debug(f"Incident participant announcement message sent.")


def send_incident_commander_readded_notification(incident_id: int, db_session: SessionLocal):
    """Sends a notification about re-adding the incident commander to the conversation."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification

    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send(
        incident.conversation.channel_id,
        notification_text,
        INCIDENT_COMMANDER_READDED_NOTIFICATION,
        notification_type,
        commander_fullname=incident.commander.name,
    )

    log.debug(f"Incident commander readded notification sent.")


def send_incident_participant_has_role_ephemeral_message(
    assigner_email: str, assignee_contact_info: dict, assignee_role: str, incident: Incident
):
    """Sends an ephemeral message to the assigner to let them know that the assignee already has the role."""
    notification_text = "Incident Assign Role Notification"

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send_ephemeral(
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

    log.debug(f"Incident participant has role message sent.")


def send_incident_participant_role_not_assigned_ephemeral_message(
    assigner_email: str, assignee_contact_info: dict, assignee_role: str, incident: Incident
):
    """Sends an ephemeral message to the assigner to let them know that we were not able to assign the role."""
    notification_text = "Incident Assign Role Notification"

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send_ephemeral(
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

    log.debug(f"Incident participant role not assigned message sent.")


def send_incident_new_role_assigned_notification(
    assigner_contact_info: dict, assignee_contact_info: dict, assignee_role: str, incident: Incident
):
    """Notified the conversation about the new participant role."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send(
        incident.conversation.channel_id,
        notification_text,
        INCIDENT_NEW_ROLE_NOTIFICATION,
        notification_type,
        assigner_fullname=assigner_contact_info["fullname"],
        assignee_fullname=assignee_contact_info["fullname"],
        assignee_firstname=assignee_contact_info["fullname"].split(" ")[0],
        assignee_weblink=assignee_contact_info["weblink"],
        assignee_role=assignee_role,
    )

    log.debug(f"Incident new role assigned message sent.")


def send_incident_review_document_notification(
    conversation_id: str, incident_review_document_weblink: str
):
    """Sends the review document notification."""
    notification_text = "Incident Notification"
    notification_type = MessageType.incident_notification

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send(
        conversation_id,
        notification_text,
        INCIDENT_REVIEW_DOCUMENT_NOTIFICATION,
        notification_type,
        incident_review_document_weblink=incident_review_document_weblink,
    )

    log.debug(f"Incident review document notification sent.")


def send_incident_resources_ephemeral_message_to_participant(
    user_id: str, incident: Incident, db_session: SessionLocal
):
    """Sends the list of incident resources to the participant via an ephemeral message."""
    # we get the incident documents
    incident_document = get_document(
        db_session=db_session,
        incident_id=incident.id,
        resource_type=INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    )

    incident_faq = get_document(
        db_session=db_session, incident_id=incident.id, resource_type=INCIDENT_RESOURCE_FAQ_DOCUMENT
    )

    # we send the ephemeral message
    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send_ephemeral(
        incident.conversation.channel_id,
        user_id,
        "Incident Resources Message",
        INCIDENT_RESOURCES_MESSAGE,
        MessageType.incident_resources_message,
        commander_fullname=incident.commander.name,
        commander_weblink=incident.commander.weblink,
        document_weblink=incident_document.weblink,
        storage_weblink=incident.storage.weblink,
        faq_weblink=incident_faq.weblink,
    )

    log.debug(f"List of incident resources sent to {user_id} via ephemeral message.")
