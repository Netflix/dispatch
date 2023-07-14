"""
.. module: dispatch.plugins.dispatch_slack.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import Any, List, Optional

from blockkit import (
    Actions,
    Button,
    Context,
    Divider,
    MarkdownText,
    Section,
    StaticSelect,
    PlainOption,
)
from slack_sdk.web.client import WebClient
from slack_sdk.errors import SlackApiError

from dispatch.messaging.strings import (
    EVERGREEN_REMINDER_DESCRIPTION,
    INCIDENT_PARTICIPANT_SUGGESTED_READING_DESCRIPTION,
    INCIDENT_TASK_LIST_DESCRIPTION,
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    MessageType,
    render_message_template,
)
from dispatch.plugins.dispatch_slack.config import SlackConfiguration
from dispatch.plugins.dispatch_slack.enums import SlackAPIErrorCode

log = logging.getLogger(__name__)


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


def get_incident_conversation_command_message(
    command_string: str, config: Optional[SlackConfiguration] = None
) -> dict[str, str]:
    """Fetches a custom message and response type for each respective slash command."""

    default = {
        "response_type": "ephemeral",
        "text": f"Running command... `{command_string}`",
    }

    if not config:
        return default

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

    return command_messages.get(command_string, default)


def build_command_error_message(payload: dict, error: Any) -> str:
    message = f"""Unfortunately we couldn't run `{payload['command']}` due to the following reason: {str(error)}  """
    return message


def build_role_error_message(payload: dict) -> str:
    message = f"""I see you tried to run `{payload['command']}`. This is a sensitive command and cannot be run with the incident role you are currently assigned."""
    return message


def build_context_error_message(payload: dict, error: Any) -> str:
    message = (
        f"""I see you tried to run `{payload['command']}` in an non-incident conversation. Incident-specifc commands can only be run in incident conversations."""  # command_context_middleware()
        if payload.get("command")
        else str(error)  # everything else
    )
    return message


def build_bot_not_present_message(client: WebClient, command: str, conversations: dict) -> str:
    team_id = client.team_info(client)["team"]["id"]

    deep_links = [
        f"<slack://channel?team={team_id}&id={c['id']}|#{c['name']}>" for c in conversations
    ]

    message = f"""
    Looks like you tried to run `{command}` in a conversation where the Dispatch bot is not present. Add the bot to your conversation or run the command in one of the following conversations:\n\n {(", ").join(deep_links)}"""
    return message


def build_slack_api_error_message(error: SlackApiError) -> str:
    return (
        "Sorry, the request to Slack timed out. Try running your command again."
        if error.response.get("error") == SlackAPIErrorCode.VIEW_EXPIRED
        else "Sorry, we've run into an unexpected error with Slack."
    )


def build_unexpected_error_message(guid: str) -> str:
    message = f"""Sorry, we've run into an unexpected error. \
For help please reach out to your Dispatch admins and provide them with the following token: `{guid}`"""
    return message


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
    blocks = [Divider()]
    for item in items:
        if isinstance(item, list):  # handle case where we are passing multiple grouped items
            blocks += default_notification(item)

        if item.get("title_link") == "None":  # avoid adding blocks with no data
            continue

        if item.get("type"):
            if item["type"] == "context":
                blocks.append(Context(elements=[MarkdownText(text=format_default_text(item))]))
            else:
                blocks.append(Section(text=format_default_text(item)))
        else:
            blocks.append(Section(text=format_default_text(item)))

        if item.get("buttons"):
            elements = []
            for button in item["buttons"]:
                if button.get("button_text") and button.get("button_value"):
                    if button.get("button_url"):
                        element = Button(
                            action_id=button["button_action"],
                            text=button["button_text"],
                            value=button["button_value"],
                            url=button["button_url"],
                        )
                    else:
                        element = Button(
                            action_id=button["button_action"],
                            text=button["button_text"],
                            value=button["button_value"],
                        )

                    elements.append(element)
            blocks.append(Actions(elements=elements))

        if select := item.get("select"):
            options = []
            for option in select["options"]:
                element = PlainOption(text=option["option_text"], value=option["option_value"])
                options.append(element)

            static_select = []
            if select.get("placeholder"):
                static_select.append(
                    StaticSelect(
                        placeholder=select["placeholder"],
                        options=options,
                        action_id=select["select_action"],
                    )
                )
            else:
                static_select.append(
                    StaticSelect(options=options, action_id=select["select_action"])
                )
            blocks.append(Actions(elements=static_select))

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
        blocks.append(Section(text=description))

    for item in items:
        if message_template:
            rendered_items = render_message_template(message_template, **item)
            blocks += template_func(rendered_items)
        else:
            blocks += template_func(**item)["blocks"]

    blocks_grouped = []
    if items:
        if items[0].get("items_grouped"):
            for item in items[0]["items_grouped"]:
                rendered_items_grouped = render_message_template(
                    items[0]["items_grouped_template"], **item
                )
                blocks_grouped += template_func(rendered_items_grouped)

    return blocks + blocks_grouped
