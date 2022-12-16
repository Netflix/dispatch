"""
.. module: dispatch.plugins.dispatch_slack.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import List, Optional

from blockkit import Section, Divider, Button, Context, MarkdownText, PlainText, Actions

from dispatch.messaging.strings import (
    EVERGREEN_REMINDER_DESCRIPTION,
    INCIDENT_PARTICIPANT_SUGGESTED_READING_DESCRIPTION,
    INCIDENT_TASK_LIST_DESCRIPTION,
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    MessageType,
    render_message_template,
)

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
                blocks.append(PlainText(text=format_default_text(item)))
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
                            url=button["button_url"],
                        )

                    elements.append(element)
            blocks.append(Actions(elements=elements))

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
