from dispatch.config import INCIDENT_PLUGIN_CONVERSATION_SLUG
from dispatch.plugins.base import plugins


def send_feedack_to_user(channel_id: str, user_id: str, message: str):
    """Sends feedack to the user using an ephemeral message."""
    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": message}}]

    convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)
    convo_plugin.send_ephemeral(channel_id, user_id, "Conversation Command Feedback", blocks=blocks)
