"""
.. module: dispatch.plugins.google_gmail.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import base64
import logging
import os
import platform
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from tenacity import retry, stop_after_attempt

from dispatch.config import DISPATCH_HELP_EMAIL, DISPATCH_HELP_SLACK_CHANNEL
from dispatch.decorators import apply, counter, timer
from dispatch.messaging import (
    INCIDENT_TASK_REMINDER_DESCRIPTION,
    MessageType,
    render_message_template,
)
from dispatch.plugins.bases import ConversationPlugin
from dispatch.plugins.dispatch_google import gmail as google_gmail_plugin
from dispatch.plugins.dispatch_google.common import get_service
from dispatch.plugins.dispatch_google.config import (
    GOOGLE_USER_OVERRIDE,
    GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT,
)

from .filters import env


log = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3))
def send_message(service, message):
    """Sends an email message."""
    return service.users().messages().send(userId="me", body=message).execute()


def create_html_message(recipient: str, subject: str, body: str) -> Dict:
    """Creates a message for an email."""
    message = MIMEText(body, "html")

    if GOOGLE_USER_OVERRIDE:
        recipient = GOOGLE_USER_OVERRIDE
        log.warning("GOOGLE_USER_OVERIDE set. Using override.")

    message["to"] = recipient
    message["from"] = GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT
    message["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}


def get_template(message_type: MessageType):
    """Fetches the correct template based on the message type."""
    template_map = {
        MessageType.incident_notification: ("notification.html", None),
        MessageType.incident_status_report: ("status_report.html", None),
        MessageType.incident_participant_welcome: ("notification.html", None),
        MessageType.incident_task_reminder: (
            "task_notification.html",
            INCIDENT_TASK_REMINDER_DESCRIPTION,
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
        data = item.__dict__
        data.update({"name": item.incident.name, "title": item.incident.title})
        master_map.append(render_message_template(message_template, **data))

    kwargs.update({"items": master_map, "description": description})
    return template.render(**kwargs)


def create_message_body(message_template: dict, message_type: MessageType, **kwargs):
    """Creates the correct message body based on message type."""
    template, description = get_template(message_type)
    kwargs.update(
        {
            "dispatch_help_email": DISPATCH_HELP_EMAIL,
            "dispatch_help_slack_channel": DISPATCH_HELP_SLACK_CHANNEL,
        }
    )
    rendered = render_message_template(message_template, **kwargs)
    kwargs.update({"items": rendered, "description": description})
    return template.render(**kwargs)


def render_email(name, message):
    """Helper function to preview your email."""
    with open(name, "wb") as fp:
        fp.write(message.encode("utf-8"))

    if platform.system() == "Linux":
        cwd = os.getcwd()
        print(f"file:/{cwd}/{name}")
    else:
        print(
            rf"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome {name}"
        )  # noqa: W605


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleGmailConversationPlugin(ConversationPlugin):
    title = "Google Gmail - Conversation"
    slug = "google-gmail-conversation"
    description = "Uses gmail to facilitate conversations."
    version = google_gmail_plugin.__version__

    author = "Kevin Glisson"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.scopes = ["https://mail.google.com/"]

    def send(
        self,
        user: str,
        message_template: dict,
        notification_type: MessageType,
        items: Optional[List] = None,
        **kwargs,
    ):
        """Sends an html email based on the type."""
        # TODO allow for bulk sending (kglisson)
        client = get_service("gmail", "v1", self.scopes)

        if kwargs.get("subject"):
            subject = kwargs["subject"]
        else:
            subject = f"{kwargs['name'].upper()} - Incident Notification"

        if not items:
            message_body = create_message_body(message_template, notification_type, **kwargs)
        else:
            message_body = create_multi_message_body(
                message_template, notification_type, items, **kwargs
            )

        # render_email("task-reminder.html", message_body)
        html_message = create_html_message(user, subject, message_body)
        return send_message(client, html_message)
