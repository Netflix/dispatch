import logging
from typing import Union
import uuid

from http import HTTPStatus
from typing import Any

from blockkit import Modal, MarkdownText, Context
from dispatch.auth.models import DispatchUser
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.async_app import AsyncBoltContext, AsyncRespond, AsyncAck, AsyncBoltRequest
from slack_bolt.response import BoltResponse
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.client import WebClient
from sqlalchemy.orm import Session

from .decorators import message_dispatcher
from .exceptions import BotNotPresentError, RoleError, ContextError, DispatchException
from .messaging import (
    build_bot_not_present_message,
    build_context_error_message,
    build_role_error_message,
    build_unexpected_error_message,
)
from .middleware import (
    configuration_middleware,
    db_middleware,
    message_context_middleware,
    user_middleware,
)

app = AsyncApp(
    token="xoxb-valid",
    raise_error_for_unhandled_request=False,
    process_before_response=True,
    request_verification_enabled=False,  # NOTE this is only safe because we do additional verification in order to determine which plugin configuration we are using
)

logging.basicConfig(level=logging.DEBUG)


@app.error
async def app_error_handler(
    error: Any,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    body: dict,
    payload: dict,
    logger: logging.Logger,
    respond: AsyncRespond,
) -> BoltResponse:

    if body:
        logger.info(f"Request body: {body}")

    message = await build_and_log_error(client, error, logger, payload, context)

    # the user is within a modal flow
    if body.get("view"):
        modal = Modal(
            title="Error",
            close="Close",
            blocks=[Context(elements=[MarkdownText(text=message)])],
        ).build()

        await client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

    # the user is in a message flow
    if body.get("response_url"):
        await respond(text=message, response_type="ephemeral")

    if not isinstance(error, DispatchException):
        return BoltResponse(body=body, status=HTTPStatus.INTERNAL_SERVER_ERROR.value)

    # for known exceptions we return OK, prevents error messages from Slackbot
    return BoltResponse(status=HTTPStatus.OK.value)


async def build_and_log_error(
    client: AsyncWebClient,
    error: Any,
    logger: logging.Logger,
    payload: dict,
    context: AsyncBoltContext,
) -> str:
    if isinstance(error, RoleError):
        message = await build_role_error_message(payload)
        logger.info(error)

    elif isinstance(error, ContextError):
        message = await build_context_error_message(payload, error)
        logger.info(error)

    elif isinstance(error, BotNotPresentError):
        message = await build_bot_not_present_message(
            client, payload["command"], context["conversations"]
        )
        logger.info(error)
    else:
        guid = str(uuid.uuid4())
        message = await build_unexpected_error_message(guid)
        logger.exception(error, extra=dict(slack_interaction_guid=guid))

    return message


@app.event(
    {"type": "message"},
    middleware=[
        message_context_middleware,
        db_middleware,
        user_middleware,
        configuration_middleware,
    ],
)
async def handle_message_events(
    ack: AsyncAck,
    body: dict,
    client: Union[AsyncWebClient, WebClient],
    context: AsyncBoltContext,
    db_session: Session,
    payload: dict,
    respond: AsyncRespond,
    request: AsyncBoltRequest,
    user: DispatchUser,
) -> None:
    """Container function for all message functions."""
    await message_dispatcher.dispatch(**locals())
