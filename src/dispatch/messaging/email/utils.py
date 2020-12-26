import os
import subprocess
import tempfile
import platform


from dispatch.messaging.strings import (
    DOCUMENT_EVERGREEN_REMINDER_DESCRIPTION,
    INCIDENT_FEEDBACK_DAILY_DIGEST_DESCRIPTION,
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    MessageType,
    render_message_template,
)

from .filters import env


def get_template(message_type: MessageType):
    """Fetches the correct template based on the message type."""
    template_map = {
        MessageType.incident_executive_report: ("executive_report.html", None),
        MessageType.incident_notification: ("notification.html", None),
        MessageType.incident_participant_welcome: ("notification.html", None),
        MessageType.incident_tactical_report: ("tactical_report.html", None),
        MessageType.incident_task_reminder: (
            "task_notification.html",
            INCIDENT_TASK_REMINDER_DESCRIPTION,
        ),
        MessageType.document_evergreen_reminder: (
            "document_evergreen_reminder.html",
            DOCUMENT_EVERGREEN_REMINDER_DESCRIPTION,
        ),
        MessageType.incident_feedback_daily_digest: (
            "feedback_notification.html",
            INCIDENT_FEEDBACK_DAILY_DIGEST_DESCRIPTION,
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
    rendered = render_message_template(message_template, **kwargs)
    kwargs.update({"items": rendered, "description": description})
    return render_html(template.render(**kwargs))


def render_html(template):
    """Uses the mjml cli to create html."""
    with tempfile.NamedTemporaryFile() as fp:
        return subprocess.run(["mjml", fp.name, "-s"], capture_output=True)


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
