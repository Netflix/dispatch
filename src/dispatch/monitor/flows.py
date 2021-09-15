from dispatch.database.core import SessionLocal
from dispatch.plugin import service as plugin_service


def send_monitor_notification(
    project_id: int, conversation_id: int, message_template: str, db_session: SessionLocal, **kwargs
):
    """Sends a monitor notification."""
    notification_text = "Incident Notification"
    notification_type = "incident-notification"

    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="conversation", project_id=project_id
    )
    plugin.instance.send(
        conversation_id, notification_text, message_template, notification_type, **kwargs
    )
