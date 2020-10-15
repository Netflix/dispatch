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

from dispatch.conversation import service as conversation_service
from dispatch.database import get_db
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service

from . import __version__
from .actions import handle_block_action, handle_dialog_action
from .commands import command_functions
from .config import (
    SLACK_APP_USER_SLUG,
    SLACK_COMMAND_LIST_INCIDENTS_SLUG,
    SLACK_COMMAND_REPORT_INCIDENT_SLUG,
    SLACK_SIGNING_SECRET,
)
from .events import event_functions, get_channel_id_from_event, EventEnvelope
from .messaging import (
    INCIDENT_CONVERSATION_COMMAND_MESSAGE,
    create_command_run_in_conversation_where_bot_not_present_message,
    create_command_run_in_nonincident_conversation_message,
)
from .modals import handle_modal_action


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
    """Handle all incomming Slack events."""
    raw_request_body = bytes.decode(await request.body())

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # Echo the URL verification challenge code back to Slack
    if event.challenge:
        return {"challenge": event.challenge}

    event_body = event.event

    user_id = event_body.user
    channel_id = get_channel_id_from_event(event_body)

    if user_id and channel_id:
        conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
            db_session=db_session, channel_id=channel_id
        )

        if conversation and dispatch_slack_service.is_user(user_id):
            # We create an async Slack client
            slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

            # We resolve the user's email
            user_email = await dispatch_slack_service.get_user_email_async(
                slack_async_client, user_id
            )

            # Dispatch event functions to be executed in the background
            for f in event_functions(event):
                background_tasks.add_task(f, user_email, conversation.incident_id, event=event)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()
    return {"ok"}


@router.post("/slack/command")
async def handle_command(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    x_slack_request_timestamp: int = Header(None),
    x_slack_signature: str = Header(None),
    db_session: Session = Depends(get_db),
):
    """Handle all incomming Slack commands."""
    raw_request_body = bytes.decode(await request.body())
    request_body_form = await request.form()
    command_details = request_body_form._dict

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # We fetch conversation by channel id
    channel_id = command_details.get("channel_id")
    conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
        db_session=db_session, channel_id=channel_id
    )

    # We get the name of command that was run
    command = command_details.get("command")

    incident_id = 0
    if conversation:
        incident_id = conversation.incident_id
    else:
        if command not in [SLACK_COMMAND_REPORT_INCIDENT_SLUG, SLACK_COMMAND_LIST_INCIDENTS_SLUG]:
            # We let the user know that incident-specific commands
            # can only be run in incident conversations
            return create_command_run_in_nonincident_conversation_message(command)

        # We create an async Slack client
        slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

        # We get the list of public and private conversations the Slack bot is a member of
        (
            public_conversations,
            private_conversations,
        ) = await dispatch_slack_service.get_conversations_by_user_id_async(
            slack_async_client, SLACK_APP_USER_SLUG
        )

        # We get the name of conversation where the command was run
        conversation_id = command_details.get("channel_id")
        conversation_name = await dispatch_slack_service.get_conversation_name_by_id_async(
            slack_async_client, conversation_id
        )

        if (
            not conversation_name
            or conversation_name not in public_conversations + private_conversations
        ):
            # We let the user know in which public conversations they can run the command
            return create_command_run_in_conversation_where_bot_not_present_message(
                command, public_conversations
            )

    for f in command_functions(command):
        background_tasks.add_task(f, incident_id, command=command_details)

    return INCIDENT_CONVERSATION_COMMAND_MESSAGE.get(command, f"Running... Command: {command}")


@router.post("/slack/action")
async def handle_action(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    x_slack_request_timestamp: int = Header(None),
    x_slack_signature: str = Header(None),
    db_session: Session = Depends(get_db),
):
    """Handle all incomming Slack actions."""
    raw_request_body = bytes.decode(await request.body())
    request_body_form = await request.form()
    action = json.loads(request_body_form.get("payload"))

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We create an async Slack client
    slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

    # We resolve the user's email
    user_id = action["user"]["id"]
    user_email = await dispatch_slack_service.get_user_email_async(slack_async_client, user_id)

    action["user"]["email"] = user_email

    # We add the user-agent string to the response headers
    # NOTE: I don't think this header ever gets sent? (kglisson)
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # When there are no exceptions within the dialog submission, your app must respond with 200 OK with an empty body.
    response_body = {}
    if action.get("view"):
        handle_modal_action(action, background_tasks)
        if action["type"] == "view_submission":
            # For modals we set "response_action" to "clear" to close all views in the modal.
            # An empty body is currently not working.
            response_body = {"response_action": "clear"}
    elif action["type"] == "dialog_submission":
        handle_dialog_action(action, background_tasks, db_session=db_session)
    elif action["type"] == "block_actions":
        handle_block_action(action, background_tasks)

    return response_body
