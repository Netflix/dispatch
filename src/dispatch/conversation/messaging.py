from dispatch.database import SessionLocal
from dispatch.plugin import service as plugin_service


def send_feedack_to_user(channel_id: str, user_id: str, message: str, db_session: SessionLocal):
    """Sends feedack to the user using an ephemeral message."""
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": message}}]

    plugin = plugin_service.get_active(db_session=db_session, plugin_type="conversation")
    plugin.instance.send_ephemeral(
        channel_id, user_id, "Conversation Command Feedback", blocks=blocks
    )
