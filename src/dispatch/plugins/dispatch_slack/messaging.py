"""
.. module: dispatch.plugins.dispatch_slack.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import List, Optional
from jinja2 import Template

from dispatch.messaging.strings import (
    EVERGREEN_REMINDER_DESCRIPTION,
    INCIDENT_PARTICIPANT_SUGGESTED_READING_DESCRIPTION,
    INCIDENT_TASK_LIST_DESCRIPTION,
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    MessageType,
    render_message_template,
)

from .config import SlackConfiguration


log = logging.getLogger(__name__)


def get_incident_conversation_command_message(config: SlackConfiguration, command_string: str):
    command_messages = {
        config.slack_command_run_workflow: {
            "response_type": "ephemeral",
            "text": "Opening a modal to run a workflow...",
        },
        config.slack_command_report_tactical: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to write a tactical report...",
        },
        config.slack_command_list_tasks: {
            "response_type": "ephemeral",
            "text": "Fetching the list of incident tasks...",
        },
        config.slack_command_list_my_tasks: {
            "response_type": "ephemeral",
            "text": "Fetching your incident tasks...",
        },
        config.slack_command_list_participants: {
            "response_type": "ephemeral",
            "text": "Fetching the list of incident participants...",
        },
        config.slack_command_assign_role: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to assign a role to a participant...",
        },
        config.slack_command_update_incident: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to update incident information...",
        },
        config.slack_command_update_participant: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to update participant information...",
        },
        config.slack_command_engage_oncall: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to engage an oncall person...",
        },
        config.slack_command_list_resources: {
            "response_type": "ephemeral",
            "text": "Fetching the list of incident resources...",
        },
        config.slack_command_report_incident: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to report an incident...",
        },
        config.slack_command_report_executive: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to write an executive report...",
        },
        config.slack_command_update_notifications_group: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to update the membership of the notifications group...",
        },
        config.slack_command_add_timeline_event: {
            "response_type": "ephemeral",
            "text": "Opening a dialog to add an event to the incident timeline...",
        },
        config.slack_command_list_incidents: {
            "response_type": "ephemeral",
            "text": "Fetching the list of incidents...",
        },
        config.slack_command_list_workflows: {
            "response_type": "ephemeral",
            "text": "Fetching the list of workflows...",
        },
    }

    return command_messages.get(command_string, f"Running command... {command_string}")


INCIDENT_CONVERSATION_COMMAND_RUN_IN_NONINCIDENT_CONVERSATION = """
I see you tried to run `{{command}}` in an non-incident conversation.
Incident-specifc commands can only be run in incident conversations.""".replace(
    "\n", " "
).strip()

INCIDENT_CONVERSATION_COMMAND_RUN_BY_NON_PRIVILEGED_USER = """
I see you tried to run `{{command}}`.
This is a sensitive command and cannot be run with the incident role you are currently assigned.""".replace(
    "\n", " "
).strip()

INCIDENT_CONVERSATION_COMMAND_RUN_IN_CONVERSATION_WHERE_BOT_NOT_PRESENT = """
Looks like you tried to run `{{command}}` in a conversation where the Dispatch bot is not present.
Add the bot to your conversation or run the command in one of the following conversations: {{conversations}}""".replace(
    "\n", " "
).strip()


def create_command_run_by_non_privileged_user_message(command: str):
    """Creates a message for when a sensitive command is run by a non privileged user."""
    return {
        "response_type": "ephemeral",
        "text": Template(INCIDENT_CONVERSATION_COMMAND_RUN_BY_NON_PRIVILEGED_USER).render(
            command=command
        ),
    }


def create_command_run_in_nonincident_conversation_message(command: str):
    """Creates a message for when an incident specific command is run in an nonincident conversation."""
    return {
        "response_type": "ephemeral",
        "text": Template(INCIDENT_CONVERSATION_COMMAND_RUN_IN_NONINCIDENT_CONVERSATION).render(
            command=command
        ),
    }


def create_command_run_in_conversation_where_bot_not_present_message(
    command: str, conversations: List
):
    """Creates a message for when a non-incident specific command is run in a conversation where the Dispatch bot is not present."""
    conversations = (", ").join([f"#{conversation}" for conversation in conversations])
    return {
        "response_type": "ephemeral",
        "text": Template(
            INCIDENT_CONVERSATION_COMMAND_RUN_IN_CONVERSATION_WHERE_BOT_NOT_PRESENT
        ).render(command=command, conversations=conversations),
    }


def create_incident_reported_confirmation_message(
    title: str, description: str, incident_type: str, incident_priority: str
):
    """Creates an incident reported confirmation message."""
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Security Incident Reported",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "This is a confirmation that you have reported a security incident with the following information. You'll get invited to a Slack conversation soon.",
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Incident Title*: {title}"}},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Incident Description*: {description}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Incident Type*: {incident_type}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Incident Priority*: {incident_priority}"},
        },
    ]


def get_template(message_type: MessageType):
    """Fetches the correct template based on message type."""
    template_map = {
        MessageType.evergreen_reminder: (
            default_notification,
            EVERGREEN_REMINDER_DESCRIPTION,
        ),
        MessageType.incident_participant_suggested_reading: (
            default_notification,
            INCIDENT_PARTICIPANT_SUGGESTED_READING_DESCRIPTION,
        ),
        MessageType.incident_task_list: (default_notification, INCIDENT_TASK_LIST_DESCRIPTION),
        MessageType.incident_task_reminder: (
            default_notification,
            INCIDENT_TASK_REMINDER_DESCRIPTION,
        ),
    }

    return template_map.get(message_type, (default_notification, None))


def format_default_text(item: dict):
    """Creates the correct Slack text string based on the item context."""
    if item.get("title_link"):
        return f"*<{item['title_link']}|{item['title']}>*\n{item['text']}"
    if item.get("datetime"):
        return f"*{item['title']}*\n <!date^{int(item['datetime'].timestamp())}^ {{date}} | {item['datetime']}"
    if item.get("title"):
        return f"*{item['title']}*\n{item['text']}"
    return item["text"]


def default_notification(items: list):
    """Creates blocks for a default notification."""
    blocks = []
    blocks.append({"type": "divider"})
    for item in items:
        if isinstance(item, list):  # handle case where we are passing multiple grouped items
            blocks += default_notification(item)

        if item.get("title_link") == "None":  # avoid adding blocks with no data
            continue

        if item.get("type"):
            block = {
                "type": item["type"],
            }
            if item["type"] == "context":
                block.update({"elements": [{"type": "mrkdwn", "text": format_default_text(item)}]})
            else:
                block.update({"text": {"type": "plain_text", "text": format_default_text(item)}})
        else:
            block = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": format_default_text(item)},
            }

        if item.get("button_text") and item.get("button_value"):
            block.update(
                {
                    "block_id": item["button_action"],
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": item["button_text"]},
                        "value": item["button_value"],
                    },
                }
            )

        blocks.append(block)

    return blocks


def create_message_blocks(
    message_template: List[dict],
    message_type: MessageType,
    items: Optional[List] = None,
    **kwargs,
):
    """Creates all required blocks for a given message type and template."""
    if not items:
        items = []

    if kwargs:
        items.append(kwargs)  # combine items and kwargs

    template_func, description = get_template(message_type)

    blocks = []
    if description:  # include optional description text (based on message type)
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": description}})

    for item in items:
        rendered_items = render_message_template(message_template, **item)
        blocks += template_func(rendered_items)

    blocks_grouped = []
    if items:
        if items[0].get("items_grouped"):
            for item in items[0]["items_grouped"]:
                rendered_items_grouped = render_message_template(
                    items[0]["items_grouped_template"], **item
                )
                blocks_grouped += template_func(rendered_items_grouped)

    return blocks + blocks_grouped
