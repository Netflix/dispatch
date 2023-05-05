import logging
from blockkit import Modal, Section
from pydantic.error_wrappers import ValidationError
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient

from dispatch.plugins.dispatch_slack.enums import SlackAPIErrorCode

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
    """Send a success modal to a user in Slack.

    Args:
        client (WebClient): A Slack WebClient instance.
        view_id (str): The ID of the view to update.
        title (str): The title of the modal.
        trigger_id (str | None, optional): The trigger ID used to identify the source of the modal action. Defaults to None.
        message (str | None, optional): The success message to display in the modal. Defaults to "Success!".
        blocks (list[Section] | None, optional): A list of additional blocks to display in the modal. Defaults to None.
        close_title (str, optional): The title of the close button in the modal. Defaults to "Close".

    Note:
        This function catches the SlackApiError exception "not_found" and logs a warning message instead of raising the exception.
        This error usually indicates that the user closed the loading modal early and is transparent to the end user.

    Example:
        from slack_sdk import WebClient

        slack_client = WebClient(token="your_slack_bot_token")
        view_id = "your_view_id"
        title = "Success Modal"
        trigger_id = "your_trigger_id"

        send_success_modal(
            client=slack_client,
            view_id=view_id,
            title=title,
            trigger_id=trigger_id,
            message="Your request was processed successfully!",
            close_title="Close",
        )
    """
    try:
        modal = Modal(
            title=title,
            close=close_title,
            blocks=[Section(text=message)] if not blocks else blocks,
        ).build()
    except ValidationError as e:
        log.error(
            f"Blockkit raised an exception building success modal, falling back to default: {e}"
        )
        modal = Modal(
            title="Done",
            close="Close",
            blocks=[Section(text="Success!")],
        ).build()

    try:
        client.views_update(
            view_id=view_id,
            trigger_id=trigger_id if trigger_id else None,
            view=modal,
        )
    except SlackApiError as e:
        if e.response["error"] == SlackAPIErrorCode.VIEW_NOT_FOUND:
            e.add_note(
                "This error usually indicates that the user closed the loading modal early and is transparent."
            )
            log.warning(f"Failed to send success Modal: {e}")
