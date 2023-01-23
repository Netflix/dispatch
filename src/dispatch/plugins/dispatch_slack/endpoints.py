from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from slack_bolt.adapter.starlette.handler import SlackRequestHandler
from slack_sdk.signature import SignatureVerifier
from sqlalchemy import true
from starlette.requests import Request, Headers

from dispatch.database.core import refetch_db_session
from dispatch.plugin.models import Plugin, PluginInstance

from .bolt import app
from .incident.interactive import configure as incident_configure
from .feedback.interactive import *  # noqa
from .workflow import configure as workflow_configure


router = APIRouter()


async def get_body(request: Request):
    return await request.body()


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
            incident_configure(p.configuration)
            workflow_configure(p.configuration)
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
    return await handler.handle(request)


@router.post(
    "/slack/command",
)
async def slack_commands(organization: str, request: Request, body: bytes = Depends(get_body)):
    """Handle all incoming Slack commands."""
    handler = get_request_handler(request=request, body=body, organization=organization)
    return await handler.handle(request)


@router.post(
    "/slack/action",
)
async def slack_actions(request: Request, organization: str, body: bytes = Depends(get_body)):
    """Handle all incoming Slack actions."""
    handler = get_request_handler(request=request, body=body, organization=organization)
    return await handler.handle(request)


@router.post(
    "/slack/menu",
)
async def slack_menus(request: Request, organization: str, body: bytes = Depends(get_body)):
    """Handle all incoming Slack actions."""
    handler = get_request_handler(request=request, body=body, organization=organization)
    return await handler.handle(request)
