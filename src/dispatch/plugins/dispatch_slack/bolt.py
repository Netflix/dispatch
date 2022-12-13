import logging

from typing import Dict, Any, Optional

from slack_bolt.app.async_app import AsyncApp
from slack_bolt.response import BoltResponse
from slack_bolt.request import BoltRequest
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler


from fastapi import APIRouter

from starlette.requests import Request
from starlette.responses import Response

from .listeners import MultiMessageListener

app = AsyncApp(token="xoxb-valid", raise_error_for_unhandled_request=True)
router = APIRouter()

# app.use(MultiMessageListener)

logging.basicConfig(level=logging.DEBUG)


@app.error
async def errors(error, body, context, logger, respond):
    logger.exception(error)
    logger.debug(error)
    from pprint import pprint

    pprint(body)


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
