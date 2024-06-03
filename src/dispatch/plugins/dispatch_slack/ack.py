from blockkit import Modal, Section
from slack_bolt import Ack


def ack_submission_event(ack: Ack, title: str, close: str, text: str) -> None:
    """Handles event acknowledgment."""
    ack(
        response_action="update",
        view=Modal(
            title=title,
            close=close,
            blocks=[Section(text=text)],
        ).build(),
    )
