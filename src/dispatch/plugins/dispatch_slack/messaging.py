"""
.. module: dispatch.plugins.dispatch_slack.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import List, Optional
from jinja2 import Template

from dispatch.messaging import (
    INCIDENT_TASK_LIST_DESCRIPTION,
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    MessageType,
    render_message_template,
)

from .config import (
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
    SLACK_COMMAND_LIST_RESOURCES_SLUG,
    SLACK_COMMAND_LIST_TASKS_SLUG,
    SLACK_COMMAND_MARK_ACTIVE_SLUG,
    SLACK_COMMAND_MARK_CLOSED_SLUG,
    SLACK_COMMAND_MARK_STABLE_SLUG,
    SLACK_COMMAND_STATUS_REPORT_SLUG,
)


logger = logging.getLogger(__name__)


INCIDENT_CONVERSATION_STATUS_REPORT_SUGGESTION = (
    f"Consider providing a status report using the `{SLACK_COMMAND_STATUS_REPORT_SLUG}` command"
)

INCIDENT_CONVERSATION_COMMAND_MESSAGE = {
    SLACK_COMMAND_MARK_ACTIVE_SLUG: {
        "response_type": "ephemeral",
        "text": f"The command `{SLACK_COMMAND_MARK_ACTIVE_SLUG}` has been deprecated. Please use `{SLACK_COMMAND_UPDATE_INCIDENT_SLUG}` instead.",
    },
    SLACK_COMMAND_MARK_STABLE_SLUG: {
        "response_type": "ephemeral",
        "text": f"The command `{SLACK_COMMAND_MARK_STABLE_SLUG}` has been deprecated. Please use `{SLACK_COMMAND_UPDATE_INCIDENT_SLUG}` instead.",
    },
    SLACK_COMMAND_MARK_CLOSED_SLUG: {
        "response_type": "ephemeral",
        "text": f"The command `{SLACK_COMMAND_MARK_CLOSED_SLUG}` has been deprecated. Please use `{SLACK_COMMAND_UPDATE_INCIDENT_SLUG}` instead.",
    },
    SLACK_COMMAND_STATUS_REPORT_SLUG: {
        "response_type": "ephemeral",
        "text": "Opening a dialog to write a status report...",
    },
    SLACK_COMMAND_LIST_TASKS_SLUG: {
        "response_type": "ephemeral",
        "text": "Fetching the list of incident tasks...",
    },
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG: {
        "response_type": "ephemeral",
        "text": "Fetching the list of incident participants...",
    },
    SLACK_COMMAND_ASSIGN_ROLE_SLUG: {
        "response_type": "ephemeral",
        "text": "Opening a dialog to assign a role to a participant...",
    },
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG: {
        "response_type": "ephemeral",
        "text": "Opening a dialog to update incident information...",
    },
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG: {
        "response_type": "ephemeral",
        "text": "Opening a dialog to engage an oncall person...",
    },
    SLACK_COMMAND_LIST_RESOURCES_SLUG: {
        "response_type": "ephemeral",
        "text": "Listing all incident resources...",
    },
}

INCIDENT_CONVERSATION_NON_INCIDENT_CONVERSATION_COMMAND_ERROR = """
Looks like you tried to run `{{command}}` in an non-incident conversation. You can only run Dispatch commands in incident conversations.""".replace(
    "\n", " "
).strip()


def render_non_incident_conversation_command_error_message(command: str):
    """Renders a non-incident conversation command error ephemeral message."""
    return {
        "response_type": "ephemeral",
        "text": Template(INCIDENT_CONVERSATION_NON_INCIDENT_CONVERSATION_COMMAND_ERROR).render(
            command=command
        ),
    }


def get_template(message_type: MessageType):
    """Fetches the correct template based on message type."""
    template_map = {
        MessageType.incident_notification: (default_notification, None),
        MessageType.incident_participant_welcome: (default_notification, None),
        MessageType.incident_resources_message: (default_notification, None),
        MessageType.incident_status_report: (default_notification, None),
        MessageType.incident_task_reminder: (
            default_notification,
            INCIDENT_TASK_REMINDER_DESCRIPTION,
        ),
        MessageType.incident_task_list: (default_notification, INCIDENT_TASK_LIST_DESCRIPTION),
    }

    template_func, description = template_map.get(message_type, (None, None))

    if not template_func:
        raise Exception(f"Unable to determine template. MessageType: {message_type}")

    return template_func, description


def format_default_text(item: dict):
    """Creates the correct slack text string based on the item context."""
    if item.get("title_link"):
        return f"*<{item['title_link']}|{item['title']}>*\n{item['text']}"
    if item.get("datetime"):
        return f"*{item['title']}* \n <!date^{int(item['datetime'].timestamp())}^ {{date}} | {item['datetime']}"
    return f"*{item['title']}*\n{item['text']}"


def default_notification(items: list):
    """This is a default dispatch slack notification."""
    blocks = []
    blocks.append({"type": "divider"})
    for item in items:
        if isinstance(item, list):  # handle case where we are passing multiple grouped items
            blocks += default_notification(item)

        block = {"type": "section", "text": {"type": "mrkdwn", "text": format_default_text(item)}}

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
    message_template: List[dict], message_type: MessageType, items: Optional[List] = None, **kwargs
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

    return blocks


def slack_preview(message, block=None):
    """Helper function that will generate a preview link to see what your slack message will look like."""
    from urllib.parse import quote_plus
    import json

    message = quote_plus(json.dumps(message))
    if block:
        print(f"https://api.slack.com/tools/block-kit-builder?blocks={message}")
    else:
        print(f"https://api.slack.com/docs/messages/builder?msg={message}")
