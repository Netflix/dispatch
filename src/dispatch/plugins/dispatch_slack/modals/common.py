import logging
from blockkit import Modal, Section
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient

log = logging.getLogger(__file__)


def send_success_modal(
    client: WebClient,
    view_id: str,
    title: str,
    trigger_id: str | None = None,
    message: str | None = "Success!",
    blocks: list[Section] | None = None,
    close_title: str = "Close",
) -> None:
    modal = Modal(
        title=title,
        close=close_title,
        blocks=[Section(text=message)] if not blocks else blocks,
    ).build()

    try:
        client.views_update(
            view_id=view_id,
            trigger_id=trigger_id if trigger_id else None,
            view=modal,
        )
    except SlackApiError as e:
        if e.response["error"] == "not_found":
            e.add_note("This error usually indicates that the user closed the loading modal early and is transparent.")
            log.warning(f"Failed to send success Modal: {e}")
