import logging
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from slack_bolt.response import BoltResponse


from fastapi import APIRouter

from starlette.requests import Request

from .exceptions import ContextError, RoleError

app = AsyncApp(
    token="xoxb-valid", raise_error_for_unhandled_request=True, process_before_response=True
)
router = APIRouter()

logging.basicConfig(level=logging.DEBUG)


@app.error
async def errors(ack, error, body, respond, logger):

    print(error)

    message = "An unknown error has occured."
    if isinstance(error, ContextError):
        message = str(error)

    elif isinstance(error, RoleError):
        message = str(error)

    if body.get("view"):
        pass

    else:
        await respond(text=message, response_type="ephemeral")

    logger.debug(body)
    from pprint import pprint

    pprint(body)
    logger.exception(error)
    logger.debug(error)
    return BoltResponse(status=200, body="")


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
