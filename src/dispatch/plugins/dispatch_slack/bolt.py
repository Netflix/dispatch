import logging

from http import HTTPStatus
from typing import Any

from blockkit import Modal, MarkdownText, Context
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.async_app import AsyncRespond
from slack_bolt.response import BoltResponse
from slack_sdk.web.async_client import AsyncWebClient

from .decorators import message_dispatcher
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
    body: dict,
    logger: logging.Logger,
    respond: AsyncRespond,
) -> BoltResponse:

    if body:
        logger.info(f"Request body: {body}")

    if error:
        logger.exception(f"Error: {error}")

    # the user is within a modal flow
    if body.get("view"):
        modal = Modal(
            title="Error",
            close="Close",
            blocks=[
                Context(
                    elements=[
                        MarkdownText(text=f"❌ An internal error occured:\n ```{str(error)}```")
                    ]
                )
            ],
        ).build()

        await client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

    # the user is in a message flow
    if body.get("response_url"):
        await respond(text=str(error), response_type="ephemeral")

    return BoltResponse(body=body, status=HTTPStatus.INTERNAL_SERVER_ERROR.value)


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
    ack, payload, context, body, client, respond, user, db_session
) -> None:
    """Container function for all message functions."""
    await message_dispatcher.dispatch(**locals())
