import hashlib
import hmac
import json
import logging
import platform
import sys

from time import time

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException

from sqlalchemy import true

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from dispatch.plugin.models import PluginInstance

from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.decorators import get_organization_scope_from_slug

from . import __version__
from .actions import handle_slack_action
from .commands import handle_slack_command
from .events import handle_slack_event, EventEnvelope
from .menus import handle_slack_menu


router = APIRouter()

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


def verify_signature(
    organization: str, signing_secret: str, request_data, timestamp: int, signature: str
):
    """Verifies the request signature using the app's signing secret."""
    req = f"v0:{timestamp}:{request_data}".encode("utf-8")
    slack_signing_secret = bytes(signing_secret, "utf-8")
    h = hmac.new(slack_signing_secret, req, hashlib.sha256).hexdigest()

    session = get_organization_scope_from_slug(organization)
    plugin_instances = (
        session.query(PluginInstance)
        .filter(PluginInstance.enabled == true(), PluginInstance.slug == "slack-conversation")
        .all()
    )
    signatures = [p.instance.configuration.signing_secret for p in plugin_instances]
    for signature in signatures:
        result = hmac.compare_digest(f"v0={h}", signature)
        if result:
            return

    raise HTTPException(status_code=403, detail=[{"msg": "Invalid request signature"}])


def verify_timestamp(timestamp: int):
    """Verifies that the timestamp does not differ from local time by more than five minutes."""
    if abs(time() - timestamp) > 60 * 5:
        raise HTTPException(status_code=403, detail=[{"msg": "Invalid request timestamp"}])


@router.post(
    "/{organization}/slack/event",
)
async def handle_event(
    event: EventEnvelope,
    request: Request,
    response: Response,
    organization: str,
    background_tasks: BackgroundTasks,
    x_slack_request_timestamp: int = Header(...),
    x_slack_signature: str = Header(...),
):
    """Handle all incoming Slack events."""
    raw_request_body = bytes.decode(await request.body())

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(organization, raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # Echo the URL verification challenge code back to Slack
    if event.challenge:
        return JSONResponse(content={"challenge": event.challenge})

    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    body = await handle_slack_event(
        client=slack_async_client,
        event=event,
        background_tasks=background_tasks,
    )

    return JSONResponse(content=body)


@router.post(
    "/{organization}/slack/command",
)
async def handle_command(
    request: Request,
    response: Response,
    organization: str,
    background_tasks: BackgroundTasks,
    x_slack_request_timestamp: int = Header(...),
    x_slack_signature: str = Header(...),
):
    """Handle all incoming Slack commands."""
    raw_request_body = bytes.decode(await request.body())
    request_body_form = await request.form()
    request = request_body_form._dict

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(organization, raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    body = await handle_slack_command(
        client=slack_async_client,
        request=request,
        background_tasks=background_tasks,
    )

    return JSONResponse(content=body)


@router.post(
    "/{organization}/slack/action",
)
async def handle_action(
    request: Request,
    response: Response,
    organization: str,
    background_tasks: BackgroundTasks,
    x_slack_request_timestamp: int = Header(...),
    x_slack_signature: str = Header(...),
):
    """Handle all incoming Slack actions."""
    raw_request_body = bytes.decode(await request.body())
    request_body_form = await request.form()
    try:
        request = json.loads(request_body_form.get("payload"))
    except Exception:
        raise HTTPException(status_code=400, detail=[{"msg": "Bad Request"}])

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(organization, raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # We create an async Slack client
    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    body = await handle_slack_action(
        client=slack_async_client,
        request=request,
        background_tasks=background_tasks,
    )
    return JSONResponse(content=body)


@router.post(
    "/{organization}/slack/menu",
)
async def handle_menu(
    request: Request,
    response: Response,
    organization: str,
    x_slack_request_timestamp: int = Header(...),
    x_slack_signature: str = Header(...),
):
    """Handle all incoming Slack actions."""
    raw_request_body = bytes.decode(await request.body())
    request_body_form = await request.form()
    try:
        request = json.loads(request_body_form.get("payload"))
    except Exception:
        raise HTTPException(status_code=400, detail=[{"msg": "Bad Request"}])

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(organization, raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # We create an async Slack client
    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    body = await handle_slack_menu(
        client=slack_async_client,
        request=request,
    )
    return JSONResponse(content=body)
