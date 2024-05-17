import logging
import uuid
from http import HTTPStatus
from typing import Any

from blockkit import Context, MarkdownText, Modal
from slack_bolt.app import App
from slack_bolt import Ack, BoltContext, BoltRequest, Respond
from slack_bolt.response import BoltResponse
from slack_sdk.web.client import WebClient
from slack_sdk.errors import SlackApiError
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser

from .decorators import message_dispatcher
from .exceptions import BotNotPresentError, ContextError, DispatchException, RoleError, CommandError
from .messaging import (
    build_command_error_message,
    build_bot_not_present_message,
    build_context_error_message,
    build_role_error_message,
    build_slack_api_error_message,
    build_unexpected_error_message,
)
from .middleware import (
    configuration_middleware,
    message_context_middleware,
    user_middleware,
    select_context_middleware,
)

app = App(token="xoxb-valid", request_verification_enabled=False, token_verification_enabled=False)
logging.basicConfig(level=logging.DEBUG)


@app.error
def app_error_handler(
    error: Any,
    client: WebClient,
    context: BoltContext,
    body: dict,
    payload: dict,
    logger: logging.Logger,
    respond: Respond,
) -> BoltResponse:
    if body:
        logger.info(f"Request body: {body}")

    message = build_and_log_error(client, error, logger, payload, context)

    # if we have a parent view available
    if context.get("parentView"):
        modal = Modal(
            title="Error",
            close="Close",
            blocks=[Context(elements=[MarkdownText(text=message)])],
        ).build()

        client.views_update(
            view_id=context["parentView"]["id"],
            view=modal,
        )
        return

    # the user is within a modal flow
    if body.get("view"):
        modal = Modal(
            title="Error",
            close="Close",
            blocks=[Context(elements=[MarkdownText(text=message)])],
        ).build()

        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )
        return

    # the user is in a message flow
    if body.get("response_url"):
        # the user is in a thread
        if thread := body.get("container", {}).get("thread_ts"):
            client.chat_postEphemeral(
                channel=context["channel_id"],
                text=message,
                thread_ts=thread,
                user=context["user_id"],
            )
        else:
            respond(text=message, response_type="ephemeral", replace_original=False)

    if not isinstance(error, DispatchException):
        return BoltResponse(body=body, status=HTTPStatus.INTERNAL_SERVER_ERROR.value)

    # for known exceptions we return OK, prevents error messages from Slackbot
    return BoltResponse(status=HTTPStatus.OK.value)


def build_and_log_error(
    client: WebClient,
    error: Any,
    logger: logging.Logger,
    payload: dict,
    context: BoltContext,
) -> str:
    if isinstance(error, RoleError):
        message = build_role_error_message(payload)
        logger.info(error)

    elif isinstance(error, CommandError):
        message = build_command_error_message(payload, error)
        logger.info(error)

    elif isinstance(error, ContextError):
        message = build_context_error_message(payload, error)
        logger.info(error)

    elif isinstance(error, BotNotPresentError):
        message = build_bot_not_present_message(
            client, payload["command"], context["conversations"]
        )
        logger.info(error)

    elif isinstance(error, SlackApiError):
        message = build_slack_api_error_message(error)
        logger.exception(error)

    else:
        guid = str(uuid.uuid4())
        message = build_unexpected_error_message(guid)
        logger.exception(error, extra={"slack_interaction_guid": guid})

    return message


@app.event(
    {"type": "message"},
    middleware=[
        message_context_middleware,
        user_middleware,
        configuration_middleware,
        select_context_middleware,
    ],
)
def handle_message_events(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    payload: dict,
    respond: Respond,
    request: BoltRequest,
    user: DispatchUser,
) -> None:
    """Container function for all message functions."""
    message_dispatcher.dispatch(**locals())
