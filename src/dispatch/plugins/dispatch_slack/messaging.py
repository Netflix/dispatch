"""
.. module: dispatch.plugins.dispatch_slack.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import List, Optional
from jinja2 import Template

from dispatch.incident.enums import IncidentSlackViewBlockId
from dispatch.messaging import (
    INCIDENT_TASK_LIST_DESCRIPTION,
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    INCIDENT_PARTICIPANT_SUGGESTED_READING_DESCRIPTION,
    MessageType,
    render_message_template,
)

from .config import (
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_EXECUTIVE_REPORT_SLUG,
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
    SLACK_COMMAND_LIST_RESOURCES_SLUG,
    SLACK_COMMAND_LIST_TASKS_SLUG,
    SLACK_COMMAND_REPORT_INCIDENT_SLUG,
    SLACK_COMMAND_TACTICAL_REPORT_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
)


logger = logging.getLogger(__name__)


INCIDENT_CONVERSATION_TACTICAL_REPORT_SUGGESTION = f"Consider providing a tactical report using the `{SLACK_COMMAND_TACTICAL_REPORT_SLUG}` command."

INCIDENT_CONVERSATION_COMMAND_MESSAGE = {
    SLACK_COMMAND_TACTICAL_REPORT_SLUG: {
        "response_type": "ephemeral",
        "text": "Opening a dialog to write a tactical report...",
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
    SLACK_COMMAND_REPORT_INCIDENT_SLUG: {
        "response_type": "ephemeral",
        "text": "Opening a dialog to report an incident...",
    },
    SLACK_COMMAND_EXECUTIVE_REPORT_SLUG: {
        "response_type": "ephemeral",
        "text": "Opening a dialog to write an executive report...",
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
        MessageType.incident_executive_report: (default_notification, None),
        MessageType.incident_notification: (default_notification, None),
        MessageType.incident_participant_welcome: (default_notification, None),
        MessageType.incident_resources_message: (default_notification, None),
        MessageType.incident_tactical_report: (default_notification, None),
        MessageType.incident_participant_suggested_reading: (
            default_notification,
            INCIDENT_PARTICIPANT_SUGGESTED_READING_DESCRIPTION,
        ),
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
    """Creates the correct Slack text string based on the item context."""
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


def create_block_option_from_template(text: str, value: str):
    """Helper function which generates the option block for modals / views"""
    return {"text": {"type": "plain_text", "text": str(text), "emoji": True}, "value": str(value)}


def create_modal_content(
    channel_id: str = None, incident_types: list = None, incident_priorities: list = None
):
    """Helper function which generates the slack modal / view message for (Create / start a new Incident) call"""
    incident_type_options = []
    incident_priority_options = []

    # below fields for incident type and priority are the same
    # (label and value) are set from the caller function create_incident_open_modal
    # if the value needs to be changed in the future to ID (from name to id) then modify them in the caller function

    for incident_type in incident_types:
        incident_type_options.append(
            create_block_option_from_template(
                text=incident_type.get("label"), value=incident_type.get("value")
            )
        )

    for incident_priority in incident_priorities:
        incident_priority_options.append(
            create_block_option_from_template(
                text=incident_priority.get("label"), value=incident_priority.get("value")
            )
        )

    modal_view_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Security Incident Report"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "If you suspect a security incident and require help from security, "
                        "please fill out the following to the best of your abilities.",
                    }
                ],
            },
            {
                "block_id": IncidentSlackViewBlockId.title,
                "type": "input",
                "label": {"type": "plain_text", "text": "Title"},
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "A brief explanatory title. You can change this later.",
                    },
                },
            },
            {
                "block_id": IncidentSlackViewBlockId.description,
                "type": "input",
                "label": {"type": "plain_text", "text": "Description"},
                "element": {
                    "type": "plain_text_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "A summary of what you know so far. It's all right if this is incomplete.",
                    },
                    "multiline": True,
                },
            },
            {
                "block_id": IncidentSlackViewBlockId.type,
                "type": "input",
                "label": {"type": "plain_text", "text": "Type"},
                "element": {
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select Incident Type"},
                    "options": incident_type_options,
                },
            },
            {
                "block_id": IncidentSlackViewBlockId.priority,
                "type": "input",
                "label": {"type": "plain_text", "text": "Priority", "emoji": True},
                "element": {
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": "Select Incident Priority"},
                    "options": incident_priority_options,
                },
            },
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "private_metadata": channel_id,
    }

    return modal_view_template


def create_incident_reported_confirmation_msg(
    title: str, incident_type: str, incident_priority: str
):
    return [
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
            "text": {"type": "mrkdwn", "text": f"*Incident Type*: {incident_type}"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Incident Priority*: {incident_priority}"},
        },
    ]
