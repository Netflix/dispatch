import os
import logging
import subprocess
import tempfile
import platform

from dispatch.config import MJML_PATH


from dispatch.messaging.strings import (
    DOCUMENT_EVERGREEN_REMINDER_DESCRIPTION,
    INCIDENT_DAILY_REPORT_DESCRIPTION,
    INCIDENT_FEEDBACK_DAILY_REPORT_DESCRIPTION,
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    MessageType,
    render_message_template,
)

from .filters import env

log = logging.getLogger(__name__)


def get_template(message_type: MessageType):
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
        MessageType.document_evergreen_reminder: (
            "notification_list.mjml",
            DOCUMENT_EVERGREEN_REMINDER_DESCRIPTION,
        ),
        MessageType.incident_feedback_daily_digest: (
            "notification_list.mjml",
            INCIDENT_FEEDBACK_DAILY_REPORT_DESCRIPTION,
        ),
        MessageType.incident_daily_report: (
            "notification_list.mjml",
            INCIDENT_DAILY_REPORT_DESCRIPTION,
        ),
    }

    template_path, description = template_map.get(message_type, (None, None))

    if not template_path:
        raise Exception(f"Unable to determine template. MessageType: {message_type}")

    return env.get_template(os.path.join("templates", template_path)), description


def create_multi_message_body(
    message_template: dict, message_type: MessageType, items: list, **kwargs
):
    """Creates a multi message message body based on message type."""
    template, description = get_template(message_type)

    master_map = []
    for item in items:
        master_map.append(render_message_template(message_template, **item))

    kwargs.update({"items": master_map, "description": description})
    return render_html(template.render(**kwargs))


def create_message_body(message_template: dict, message_type: MessageType, **kwargs):
    """Creates the correct message body based on message type."""
    template, description = get_template(message_type)

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


def preview_email(name, html_message):
    """Helper function to preview your email."""
    with open(name, "wb") as fp:
        fp.write(html_message.encode("utf-8"))

    if platform.system() == "Linux":
        cwd = os.getcwd()
        print(f"file:/{cwd}/{name}")
    else:
        print(
            rf"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome {name}"
        )  # noqa: W605
