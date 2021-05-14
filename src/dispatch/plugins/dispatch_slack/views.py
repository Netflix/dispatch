import hashlib
import hmac
import json
import logging
import platform
import sys

from time import time

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException

from sqlalchemy.orm import Session

from starlette.requests import Request
from starlette.responses import Response

from dispatch.database.core import get_db
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service

from . import __version__
from .actions import handle_slack_action
from .commands import handle_slack_command
from .config import SLACK_SIGNING_SECRET
from .events import handle_slack_event, EventEnvelope
from .menus import handle_slack_menu


router = APIRouter()
slack_client = dispatch_slack_service.create_slack_client()
log = logging.getLogger(__name__)


class SlackEventAppException(Exception):
    pass


def create_ua_string():
    client_name = __name__.split(".")[0]
    client_version = __version__  # Version is returned from _version.py

    # Collect the package info, Python version and OS version.
    package_info = {
        "client": "{0}/{1}".format(client_name, client_version),
        "python": "Python/{v.major}.{v.minor}.{v.micro}".format(v=sys.version_info),
        "system": "{0}/{1}".format(platform.system(), platform.release()),
    }

    # Concatenate and format the user-agent string to be passed into request headers
    ua_string = []
    for _, val in package_info.items():
        ua_string.append(val)

    return " ".join(ua_string)


def verify_signature(request_data, timestamp: int, signature: str):
    """Verifies the request signature using the app's signing secret."""
    req = f"v0:{timestamp}:{request_data}".encode("utf-8")
    slack_signing_secret = bytes(str(SLACK_SIGNING_SECRET), "utf-8")
    h = hmac.new(slack_signing_secret, req, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(f"v0={h}", signature):
        raise HTTPException(status_code=403, detail="Invalid request signature")


def verify_timestamp(timestamp: int):
    """Verifies that the timestamp does not differ from local time by more than five minutes."""
    if abs(time() - timestamp) > 60 * 5:
        raise HTTPException(status_code=403, detail="Invalid request timestamp")


@router.post("/slack/event")
async def handle_event(
    event: EventEnvelope,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    x_slack_request_timestamp: int = Header(None),
    x_slack_signature: str = Header(None),
    db_session: Session = Depends(get_db),
):
    """Handle all incoming Slack events."""
    raw_request_body = bytes.decode(await request.body())

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # Echo the URL verification challenge code back to Slack
    if event.challenge:
        return {"challenge": event.challenge}

    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    return await handle_slack_event(
        db_session=db_session,
        client=slack_async_client,
        event=event,
        background_tasks=background_tasks,
    )


@router.post("/slack/command")
async def handle_command(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    x_slack_request_timestamp: int = Header(None),
    x_slack_signature: str = Header(None),
    db_session: Session = Depends(get_db),
):
    """Handle all incoming Slack commands."""
    raw_request_body = bytes.decode(await request.body())
    request_body_form = await request.form()
    request = request_body_form._dict

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    return await handle_slack_command(
        db_session=db_session,
        client=slack_async_client,
        request=request,
        background_tasks=background_tasks,
    )


@router.post("/slack/action")
async def handle_action(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    x_slack_request_timestamp: int = Header(None),
    x_slack_signature: str = Header(None),
    db_session: Session = Depends(get_db),
):
    """Handle all incoming Slack actions."""
    raw_request_body = bytes.decode(await request.body())
    request_body_form = await request.form()
    request = json.loads(request_body_form.get("payload"))

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # We create an async Slack client
    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    return await handle_slack_action(
        db_session=db_session,
        client=slack_async_client,
        request=request,
        background_tasks=background_tasks,
    )


@router.post("/slack/menu")
async def handle_menu(
    request: Request,
    response: Response,
    x_slack_request_timestamp: int = Header(None),
    x_slack_signature: str = Header(None),
    db_session: Session = Depends(get_db),
):
    """Handle all incoming Slack actions."""
    raw_request_body = bytes.decode(await request.body())
    request_body_form = await request.form()
    request = json.loads(request_body_form.get("payload"))

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # We create an async Slack client
    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    return await handle_slack_menu(
        db_session=db_session,
        client=slack_async_client,
        request=request,
    )
