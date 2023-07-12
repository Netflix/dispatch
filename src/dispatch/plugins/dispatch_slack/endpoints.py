from http import HTTPStatus
import json

from fastapi import APIRouter, HTTPException, Depends
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse
from slack_sdk.signature import SignatureVerifier
from sqlalchemy import true
from starlette.requests import Request, Headers

from dispatch.database.core import refetch_db_session
from dispatch.plugin.models import Plugin, PluginInstance

from .bolt import app
from .case.interactive import configure as case_configure
from .handler import SlackRequestHandler
from .incident.interactive import configure as incident_configure
from .feedback.interactive import configure as feedback_configure
from .workflow import configure as workflow_configure
from .messaging import get_incident_conversation_command_message

router = APIRouter()


async def get_body(request: Request):
    return await request.body()


async def parse_request(request: Request):
    request_body_form = await request.form()
    try:
        request = json.loads(request_body_form.get("payload"))
    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail=[{"msg": "Bad Request"}]
        ) from None
    return request


def is_current_configuration(
    body: bytes, headers: Headers, plugin_instance: PluginInstance
) -> bool:
    """Uses the signing secret to determine which configuration to use."""

    verifier = SignatureVerifier(
        signing_secret=plugin_instance.configuration.signing_secret.get_secret_value()
    )

    return verifier.is_valid_request(body, headers)


def get_request_handler(request: Request, body: bytes, organization: str) -> SlackRequestHandler:
    """Creates a slack request handler for use by the api."""
    session = refetch_db_session(organization)
    plugin_instances: list[PluginInstance] = (
        session.query(PluginInstance)
        .join(Plugin)
        .filter(PluginInstance.enabled == true(), Plugin.slug == "slack-conversation")
        .all()
    )
    for p in plugin_instances:
        if is_current_configuration(body=body, headers=request.headers, plugin_instance=p):
            case_configure(p.configuration)
            feedback_configure(p.configuration)
            incident_configure(p.configuration)
            workflow_configure(p.configuration)
            app._configuration = p.configuration
            app._token = p.configuration.api_bot_token.get_secret_value()
            app._signing_secret = p.configuration.signing_secret.get_secret_value()
            session.close()
            return SlackRequestHandler(app)

    session.close()
    raise HTTPException(
        status_code=HTTPStatus.FORBIDDEN.value, detail=[{"msg": "Invalid request signature"}]
    )


@router.post(
    "/slack/event",
)
async def slack_events(request: Request, organization: str, body: bytes = Depends(get_body)):
    """Handle all incoming Slack events."""
    handler = get_request_handler(request=request, body=body, organization=organization)
    task = BackgroundTask(handler.handle, req=request, body=body)
    return JSONResponse(
        background=task,
        content=HTTPStatus.OK.phrase,
        status_code=HTTPStatus.OK,
    )


@router.post(
    "/slack/command",
)
async def slack_commands(organization: str, request: Request, body: bytes = Depends(get_body)):
    """Handle all incoming Slack commands."""
    # We build the background task
    handler = get_request_handler(request=request, body=body, organization=organization)
    task = BackgroundTask(
        handler.handle,
        req=request,
        body=body,
    )

    # We get the name of command that was run
    request_body_form = await request.form()
    command = request_body_form._dict.get("command")
    message = get_incident_conversation_command_message(
        config=app._configuration, command_string=command
    )
    return JSONResponse(
        background=task,
        content=message,
        status_code=HTTPStatus.OK,
    )


@router.post(
    "/slack/action",
)
async def slack_actions(request: Request, organization: str, body: bytes = Depends(get_body)):
    """Handle all incoming Slack actions."""
    handler = get_request_handler(request=request, body=body, organization=organization)
    return handler.handle(req=request, body=body)


@router.post(
    "/slack/menu",
)
async def slack_menus(request: Request, organization: str, body: bytes = Depends(get_body)):
    """Handle all incoming Slack menus."""
    handler = get_request_handler(request=request, body=body, organization=organization)
    return handler.handle(req=request, body=body)
