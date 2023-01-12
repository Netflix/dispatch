from fastapi import APIRouter, HTTPException
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from slack_sdk.signature import SignatureVerifier
from sqlalchemy import true
from starlette.requests import Request

from dispatch.plugin.models import Plugin, PluginInstance
from dispatch.decorators import async_timer

from .bolt import app
from .incident.interactive import configure as incident_configure
from .service import get_organization_scope_from_slug
from .workflow import configure as workflow_configure

router = APIRouter()


async def is_current_configuration(request: Request, plugin_instance: PluginInstance) -> bool:
    """Uses the signing secret to determine which configuration to use."""
    body = bytes.decode(await request.body())

    verifier = SignatureVerifier(
        signing_secret=plugin_instance.configuration.signing_secret.get_secret_value()
    )

    return verifier.is_valid_request(body=body, headers=request.headers)


@async_timer
async def get_request_handler(request: Request, organization: str) -> AsyncSlackRequestHandler:
    """Creates a slack request handler for use by the api."""
    session = get_organization_scope_from_slug(organization)
    plugin_instances = (
        session.query(PluginInstance)
        .join(Plugin)
        .filter(PluginInstance.enabled == true(), Plugin.slug == "slack-conversation")
        .all()
    )
    for p in plugin_instances:
        if await is_current_configuration(request=request, plugin_instance=p):
            incident_configure(p.configuration)
            workflow_configure(p.configuration)
            app._token = p.configuration.api_bot_token.get_secret_value()
            app._signing_secret = p.configuration.signing_secret.get_secret_value()
            session.close()
            return AsyncSlackRequestHandler(app)

    session.close()
    raise HTTPException(status_code=403, detail=[{"msg": "Invalid request signature"}])


@router.post(
    "/slack/event",
)
async def slack_events(request: Request, organization: str):
    """Handle all incoming Slack events."""
    handler = await get_request_handler(request=request, organization=organization)
    return await handler.handle(request)


@router.post(
    "/slack/command",
)
async def slack_commands(request: Request, organization: str):
    """Handle all incoming Slack commands."""
    handler = await get_request_handler(request=request, organization=organization)
    return await handler.handle(request)


@router.post(
    "/slack/action",
)
async def slack_actions(request: Request, organization: str):
    """Handle all incoming Slack actions."""
    handler = await get_request_handler(request=request, organization=organization)
    return await handler.handle(request)


@router.post(
    "/slack/menu",
)
async def slack_menus(request: Request, organization: str):
    """Handle all incoming Slack actions."""
    handler = await get_request_handler(request=request, organization=organization)
    return await handler.handle(request)
