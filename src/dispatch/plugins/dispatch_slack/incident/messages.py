"""The file/approach to Slack message building, which leverages Bolt SDK & Blockkit SDK instead of Jinja and raw Slack API calls"""

from blockkit import (
    Context,
    Message,
    Divider,
)
from blockkit.surfaces import Block


def create_incident_channel_escalate_message() -> list[Block]:
    """Generate a escalation."""

    blocks = [
        Context(elements=["This Case has been escalated to an Incident"]),
        Divider(),
    ]

    return Message(blocks=blocks).build()["blocks"]
