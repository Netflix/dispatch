"""
.. module: dispatch.monitor.flows
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import logging

from sqlalchemy.orm import Session

from dispatch.plugin import service as plugin_service


log = logging.getLogger(__name__)


def send_monitor_notification(
    project_id: int, conversation_id: int, message_template: str, db_session: Session, **kwargs
):
    """Sends a monitor notification."""
    notification_text = "Incident Notification"
    notification_type = "incident-notification"

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="conversation"
    )
    if not plugin:
        log.warning("Monitor notification not sent. No conversation plugin enabled.")
        return

    plugin.instance.send(
        conversation_id, notification_text, message_template, notification_type, **kwargs
    )
