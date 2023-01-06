from http import HTTPStatus
import logging

from blockkit import Section, Modal
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.response import BoltResponse
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler

from fastapi import APIRouter

from starlette.requests import Request

from .decorators import message_dispatcher
from .middleware import (
    message_context_middleware,
    db_middleware,
    user_middleware,
    configuration_middleware,
)


app = AsyncApp(
    token="xoxb-valid", raise_error_for_unhandled_request=True, process_before_response=True
)
router = APIRouter()

logging.basicConfig(level=logging.DEBUG)


@app.error
async def app_error_handler(error, client, body, logger):
    if body:
        logger.info(f"Request body: {body}")

        modal = Modal(
            title="Error", close="Close", blocks=[Section(text="Something went wrong...")]
        ).build()

        await client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

    logger.exception(f"Error: {error}")
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
async def handle_message_events():
    """Container function for all message functions."""
    await message_dispatcher.dispatch(**locals())


handler = AsyncSlackRequestHandler(app)


@router.post(
    "/slack/event",
)
async def slack_events(request: Request):
    """Handle all incoming Slack events."""
    return await handler.handle(request)


@router.post(
    "/slack/command",
)
async def slack_commands(request: Request):
    """Handle all incoming Slack commands."""
    return await handler.handle(request)


@router.post(
    "/slack/action",
)
async def slack_actions(request: Request):
    """Handle all incoming Slack actions."""
    return await handler.handle(request)


@router.post(
    "/slack/menu",
)
async def slack_menus(request: Request):
    """Handle all incoming Slack actions."""
    return await handler.handle(request)
