"""
.. module: dispatch.conversation.messaging
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import logging

from sqlalchemy.orm import Session

from dispatch.plugin import service as plugin_service


log = logging.getLogger(__name__)


def send_conversation_message(
    channel_id: str, project_id: int, user_id: str, message: str, db_session: Session
):
    """Sends feedack to the user using an ephemeral message."""
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": message}}]

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="conversation"
    )

    if not plugin:
        log.warning("Conversation message not sent. No conversation plugin enabled.")
        return

    plugin.instance.send_ephemeral(
        channel_id, user_id, "Conversation Command Feedback", blocks=blocks
    )
