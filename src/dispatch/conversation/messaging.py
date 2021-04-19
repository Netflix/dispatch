from dispatch.database.core import SessionLocal
from dispatch.plugin import service as plugin_service


def send_feedack_to_user(
    channel_id: str, project_id: int, user_id: str, message: str, db_session: SessionLocal
):
    """Sends feedack to the user using an ephemeral message."""
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": message}}]

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="conversation"
    )
    plugin.instance.send_ephemeral(
        channel_id, user_id, "Conversation Command Feedback", blocks=blocks
    )
