import logging

import asyncio
from fastapi import BackgroundTasks

from slack_sdk.web.async_client import AsyncWebClient

from .actions import handle_slack_action
from .commands import handle_slack_command
from .events import handle_slack_event, EventEnvelope

log = logging.getLogger(__name__)


async def run_websocket_process(config):
    from slack_sdk.socket_mode.aiohttp import SocketModeClient
    from slack_sdk.socket_mode.response import SocketModeResponse
    from slack_sdk.socket_mode.request import SocketModeRequest

    # Initialize SocketModeClient with an app-level token + WebClient
    client = SocketModeClient(
        # This app-level token will be used only for establishing a connection
        app_token=config.socket_mode_app_token.get_secret_value(),  # xapp-A111-222-xyz
        # You will be using this WebClient for performing Web API calls in listeners
        web_client=AsyncWebClient(
            token=config.api_bot_token.get_secret_value()
        ),  # xoxb-111-222-xyz
    )

    async def process(client: SocketModeClient, req: SocketModeRequest):
        background_tasks = BackgroundTasks()

        if req.type == "events_api":
            response = await handle_slack_event(
                config=config,
                client=client.web_client,
                event=EventEnvelope(**req.payload),
                background_tasks=background_tasks,
            )

        if req.type == "slash_commands":
            response = await handle_slack_command(
                config=config,
                client=client.web_client,
                request=req.payload,
                background_tasks=background_tasks,
            )

        if req.type == "interactive":
            response = await handle_slack_action(
                config=config,
                client=client.web_client,
                request=req.payload,
                background_tasks=background_tasks,
            )

        response = SocketModeResponse(envelope_id=req.envelope_id, payload=response)
        await client.send_socket_mode_response(response)

        # run the background tasks
        await background_tasks()

    # Add a new listener to receive messages from Slack
    # You can add more listeners like this
    client.socket_mode_request_listeners.append(process)
    # Establish a WebSocket connection to the Socket Mode servers
    await client.connect()
    await asyncio.sleep(float("inf"))
