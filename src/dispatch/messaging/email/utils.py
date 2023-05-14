import logging
import os
import subprocess
import tempfile

import jinja2.exceptions
from dispatch.config import MJML_PATH


from dispatch.messaging.strings import (
    EVERGREEN_REMINDER_DESCRIPTION,
    INCIDENT_DAILY_REPORT_DESCRIPTION,
    INCIDENT_FEEDBACK_DAILY_REPORT_DESCRIPTION,
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    MessageType,
    render_message_template,
)

from .filters import env

log = logging.getLogger(__name__)


def get_template(message_type: MessageType, project_id: int):
    """Fetches the correct template based on the message type."""
    template_map = {
        MessageType.incident_executive_report: ("executive_report.mjml", None),
        MessageType.incident_notification: ("notification.mjml", None),
        MessageType.incident_participant_welcome: ("notification.mjml", None),
        MessageType.incident_tactical_report: ("tactical_report.mjml", None),
        MessageType.incident_task_reminder: (
            "notification_list.mjml",
            INCIDENT_TASK_REMINDER_DESCRIPTION,
        ),
        MessageType.evergreen_reminder: (
            "notification_list.mjml",
            EVERGREEN_REMINDER_DESCRIPTION,
        ),
        MessageType.incident_feedback_daily_report: (
            "notification_list.mjml",
            INCIDENT_FEEDBACK_DAILY_REPORT_DESCRIPTION,
        ),
        MessageType.incident_daily_report: (
            "notification_list.mjml",
            INCIDENT_DAILY_REPORT_DESCRIPTION,
        ),
    }

    template_key, description = template_map.get(message_type, (None, None))

    if not template_key:
        raise Exception(f"Unable to determine template. MessageType: {message_type}")

    try:
        template_path = os.path.join("templates", "project_id", f"{project_id}", template_key)
        template = env.get_template(template_path)
    except jinja2.exceptions.TemplateNotFound:
        template_path = os.path.join("templates", template_key)
        template = env.get_template(template_path)
    log.debug("Resolved template path: %s", template_path)

    return template, description


def create_multi_message_body(
    message_template: dict, message_type: MessageType, items: list, project_id: int, **kwargs
):
    """Creates a multi message message body based on message type."""
    template, description = get_template(message_type, project_id)

    master_map = []
    for item in items:
        master_map.append(render_message_template(message_template, **item))

    kwargs.update({"items": master_map, "description": description})
    return render_html(template.render(**kwargs))


def create_message_body(
    message_template: dict, message_type: MessageType, project_id: int, **kwargs
):
    """Creates the correct message body based on message type."""
    template, description = get_template(message_type, project_id)

    items_grouped_rendered = []
    if kwargs.get("items_grouped"):
        items_grouped_template = kwargs["items_grouped_template"]
        for item in kwargs["items_grouped"]:
            item_rendered = render_message_template(items_grouped_template, **item)
            items_grouped_rendered.append(item_rendered)

        kwargs.update({"items": items_grouped_rendered, "description": description})
        return render_html(template.render(**kwargs))

    items_rendered = render_message_template(message_template, **kwargs)
    kwargs.update({"items": items_rendered, "description": description})
    return render_html(template.render(**kwargs))


def render_html(template):
    """Uses the mjml cli to create html."""

    with tempfile.NamedTemporaryFile("w+") as fp:
        fp.write(template)
        fp.flush()
        process = subprocess.run(
            ["./mjml", fp.name, "-s"],
            cwd=MJML_PATH,
            capture_output=True,
        )
        if process.stderr:
            log.error(process.stderr.decode("utf-8"))
            raise Exception("MJML template processing failed.")
        return process.stdout.decode("utf-8")
