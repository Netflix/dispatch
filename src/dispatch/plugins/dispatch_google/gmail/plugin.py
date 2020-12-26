"""
.. module: dispatch.plugins.google_gmail.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from email.mime.text import MIMEText
from typing import Dict, List, Optional
import base64
import logging

from tenacity import retry, stop_after_attempt

from dispatch.decorators import apply, counter, timer
from dispatch.messaging.strings import (
    MessageType,
)
from dispatch.plugins.bases import EmailPlugin
from dispatch.plugins.dispatch_google import gmail as google_gmail_plugin
from dispatch.plugins.dispatch_google.common import get_service
from dispatch.plugins.dispatch_google.config import (
    GOOGLE_USER_OVERRIDE,
    GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT,
)

from dispatch.messaging.email.utils import create_message_body, create_multi_message_body


log = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(3))
def send_message(service, message: dict):
    """Sends an email message."""
    return service.users().messages().send(userId="me", body=message).execute()


def create_html_message(recipient: str, cc: str, subject: str, body: str) -> Dict:
    """Creates a message for an email."""
    message = MIMEText(body, "html")

    if GOOGLE_USER_OVERRIDE:
        recipient = cc = GOOGLE_USER_OVERRIDE
        log.warning("GOOGLE_USER_OVERIDE set. Using override.")

    message["to"] = recipient
    message["cc"] = cc
    message["from"] = GOOGLE_SERVICE_ACCOUNT_DELEGATED_ACCOUNT
    message["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleGmailEmailPlugin(EmailPlugin):
    title = "Google Gmail Plugin - Email Management"
    slug = "google-gmail-email"
    description = "Uses Gmail to facilitate emails."
    version = google_gmail_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.scopes = ["https://mail.google.com/"]

    def send(
        self,
        recipient: str,
        message_template: dict,
        notification_type: MessageType,
        items: Optional[List] = None,
        **kwargs,
    ):
        """Sends an html email based on the type."""
        # TODO allow for bulk sending (kglisson)
        client = get_service("gmail", "v1", self.scopes)

        subject = f"{kwargs['name'].upper()} - Incident Notification"
        if kwargs.get("subject"):
            subject = kwargs["subject"]

        cc = ""
        if kwargs.get("cc"):
            cc = kwargs["cc"]

        if not items:
            message_body = create_message_body(message_template, notification_type, **kwargs)
        else:
            message_body = create_multi_message_body(
                message_template, notification_type, items, **kwargs
            )

        html_message = create_html_message(recipient, cc, subject, message_body)
        return send_message(client, html_message)
