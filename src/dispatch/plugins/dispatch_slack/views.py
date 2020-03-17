import hashlib
import hmac
import json
import logging
import platform
import sys
from time import time
from typing import List

import arrow
from cachetools import TTLCache
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

from dispatch.config import INCIDENT_PLUGIN_CONTACT_SLUG
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.conversation.service import get_by_channel_id
from dispatch.database import get_db, SessionLocal
from dispatch.decorators import background_task
from dispatch.enums import Visibility
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.models import IncidentUpdate, IncidentRead, IncidentStatus
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_priority.models import IncidentPriorityType
from dispatch.incident_type import service as incident_type_service
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.base import plugins
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.service import service as service_service
from dispatch.status_report import flows as status_report_flows
from dispatch.status_report import service as status_report_service
from dispatch.task import service as task_service
from dispatch.task.models import TaskStatus

from . import __version__
from .config import (
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
    SLACK_COMMAND_LIST_RESOURCES_SLUG,
    SLACK_COMMAND_LIST_TASKS_SLUG,
    SLACK_COMMAND_MARK_ACTIVE_SLUG,
    SLACK_COMMAND_MARK_CLOSED_SLUG,
    SLACK_COMMAND_MARK_STABLE_SLUG,
    SLACK_COMMAND_STATUS_REPORT_SLUG,
    SLACK_SIGNING_SECRET,
)
from .messaging import (
    INCIDENT_CONVERSATION_COMMAND_MESSAGE,
    render_non_incident_conversation_command_error_message,
)

from .service import get_user_email

once_a_day_cache = TTLCache(maxsize=1000, ttl=60 * 60 * 24)


router = APIRouter()
slack_client = dispatch_slack_service.create_slack_client()
log = logging.getLogger(__name__)


class SlackEventAppException(Exception):
    pass


class EventBody(BaseModel):
    """Body of the Slack event."""

    channel: str = None
    channel_type: str = None
    channel_id: str = None
    file_id: str = None
    deleted_ts: float = None
    event_ts: float = None
    hidden: bool = None
    inviter: str = None
    team: str = None
    text: str = None
    type: str
    subtype: str = None
    user: str = None
    user_id: str = None


class EventEnvelope(BaseModel):
    """Envelope of the Slack event."""

    challenge: str = None
    token: str = None
    team_id: str = None
    enterprise_id: str = None
    api_app_id: str = None
    event: EventBody = None
    type: str
    event_id: str = None
    event_time: int = None
    authed_users: List[str] = []


@background_task
def add_message_to_timeline(event: EventEnvelope, incident_id: int, db_session=None):
    """Uses reaction to add messages to timelines."""
    pass


@background_task
def remove_message_from_timeline(event: EventEnvelope, incident_id: int, db_session=None):
    """Uses reaction to remove messages from timeline."""
    pass


@background_task
def add_evidence_to_storage(event: EventEnvelope, incident_id: int, db_session=None):
    """Adds evidence (e.g. files) added/shared in the conversation to storage."""
    pass


def is_business_hours(commander_tz: str):
    """Determines if it's currently office hours where the incident commander is located."""
    now = arrow.utcnow().to(commander_tz)
    return now.weekday() not in [5, 6] and now.hour < 9 and now.hour > 16


def create_cache_key(user_id: str, channel_id: str):
    """Uses information in the evenvelope to construct a caching key."""
    return f"{channel_id}-{user_id}"


@background_task
def after_hours(user_email: str, incident_id: int, db_session=None):
    """Notifies the user that this incident is current in after hours mode."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    user_id = dispatch_slack_service.resolve_user(slack_client, user_email)["id"]

    # NOTE Limitations: Does not sync across instances. Does not survive webserver restart
    cache_key = create_cache_key(user_id, incident.conversation.channel_id)
    try:
        once_a_day_cache[cache_key]
        return
    except Exception:
        pass  # we don't care if there is nothing here

    # bail early if we don't care for a given severity
    priority_types = [
        IncidentPriorityType.info,
        IncidentPriorityType.low,
        IncidentPriorityType.medium,
    ]
    if incident.incident_priority.name.lower() not in priority_types:
        return

    # get their timezone from slack
    commander_info = dispatch_slack_service.get_user_info_by_email(
        slack_client, email=incident.commander.email
    )

    commander_tz = commander_info["tz"]

    if not is_business_hours(commander_tz):
        # send ephermal message
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        (
                            f"Responses may be delayed. The current incident severity is *{incident.incident_severity.name}*"
                            f" and your message was sent outside of the incident commander's working hours (Weekdays, 9am-5pm, {commander_tz})."
                        )
                    ),
                },
            }
        ]
        dispatch_slack_service.send_ephemeral_message(
            slack_client, incident.conversation.channel_id, user_id, "", blocks=blocks
        )
        once_a_day_cache[cache_key] = True


@background_task
def list_tasks(incident_id: int, command: dict = None, db_session=None):
    """Returns the list of incident tasks to the user as an ephemeral message."""
    blocks = []
    for status in TaskStatus:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{status.value} Incident Tasks*"},
            }
        )

        tasks = task_service.get_all_by_incident_id_and_status(
            db_session=db_session, incident_id=incident_id, status=status.value
        )

        for task in tasks:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*Description:* <{task.weblink}|{task.description}>\n"
                            f"*Assignees:* {task.assignees}"
                        ),
                    },
                }
            )
        blocks.append({"type": "divider"})

    dispatch_slack_service.send_ephemeral_message(
        slack_client,
        command["channel_id"],
        command["user_id"],
        "Incident List Tasks",
        blocks=blocks,
    )


@background_task
def list_participants(incident_id: int, command: dict = None, db_session=None):
    """Returns the list of incident participants to the user as an ephemeral message."""
    blocks = []
    blocks.append(
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*Incident Participants*"}}
    )

    participants = participant_service.get_all_by_incident_id(
        db_session=db_session, incident_id=incident_id
    )

    contact_plugin = plugins.get(INCIDENT_PLUGIN_CONTACT_SLUG)

    for participant in participants:
        if participant.is_active:
            participant_email = participant.individual.email
            participant_info = contact_plugin.get(participant_email)
            participant_name = participant_info["fullname"]
            participant_team = participant_info["team"]
            participant_department = participant_info["department"]
            participant_location = participant_info["location"]
            participant_weblink = participant_info["weblink"]
            participant_avatar_url = dispatch_slack_service.get_user_avatar_url(
                slack_client, participant_email
            )
            participant_active_roles = participant_role_service.get_all_active_roles(
                db_session=db_session, participant_id=participant.id
            )
            participant_roles = []
            for role in participant_active_roles:
                participant_roles.append(role.role)

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*Name:* <{participant_weblink}|{participant_name}>\n"
                            f"*Team*: {participant_team}, {participant_department}\n"
                            f"*Location*: {participant_location}\n"
                            f"*Incident Role(s)*: {(', ').join(participant_roles)}\n"
                        ),
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": participant_avatar_url,
                        "alt_text": participant_name,
                    },
                }
            )
            blocks.append({"type": "divider"})

    dispatch_slack_service.send_ephemeral_message(
        slack_client,
        command["channel_id"],
        command["user_id"],
        "Incident List Participants",
        blocks=blocks,
    )


def create_assign_role_dialog(incident_id: int, command: dict = None):
    """Creates a dialog for assigning a role."""
    role_options = []
    for role in ParticipantRoleType:
        if role != ParticipantRoleType.participant:
            role_options.append({"label": role.value, "value": role.value})

    dialog = {
        "callback_id": command["command"],
        "title": "Assign Role",
        "submit_label": "Assign",
        "elements": [
            {
                "label": "Participant",
                "type": "select",
                "name": "participant",
                "data_source": "users",
            },
            {"label": "Role", "type": "select", "name": "role", "options": role_options},
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@background_task
def create_update_incident_dialog(incident_id: int, command: dict = None, db_session=None):
    """Creates a dialog for updating incident information."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    type_options = []
    for t in incident_type_service.get_all(db_session=db_session):
        type_options.append({"label": t.name, "value": t.name})

    priority_options = []
    for priority in incident_priority_service.get_all(db_session=db_session):
        priority_options.append({"label": priority.name, "value": priority.name})

    visibility_options = []
    for visibility in Visibility:
        visibility_options.append({"label": visibility.value, "value": visibility.value})

    status_options = []
    for status in IncidentStatus:
        status_options.append({"label": status.value, "value": status.value})

    notify_options = [{"label": "Yes", "value": "Yes"}, {"label": "No", "value": "No"}]

    dialog = {
        "callback_id": command["command"],
        "title": "Update Incident",
        "submit_label": "Save",
        "elements": [
            {"type": "textarea", "label": "Title", "name": "title", "value": incident.title},
            {
                "type": "textarea",
                "label": "Description",
                "name": "description",
                "value": incident.description,
            },
            {
                "label": "Type",
                "type": "select",
                "name": "type",
                "value": incident.incident_type.name,
                "options": type_options,
            },
            {
                "label": "Status",
                "type": "select",
                "name": "status",
                "value": incident.status,
                "options": status_options,
            },
            {
                "label": "Priority",
                "type": "select",
                "name": "priority",
                "value": incident.incident_priority.name,
                "options": priority_options,
            },
            {
                "label": "Visibility",
                "type": "select",
                "name": "visibility",
                "value": incident.visibility,
                "options": visibility_options,
            },
            {
                "label": "Notify on change",
                "type": "select",
                "name": "notify",
                "value": "Yes",
                "options": notify_options,
            },
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@background_task
def create_engage_oncall_dialog(incident_id: int, command: dict = None, db_session=None):
    """Creates a dialog to engage an oncall person."""
    oncall_services = service_service.get_all_by_status(db_session=db_session, is_active=True)

    if not oncall_services.count():
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"No oncall services have been defined. You can define them in the Dispatch UI at /services",
                },
            }
        ]
        dispatch_slack_service.send_ephemeral_message(
            slack_client,
            command["channel_id"],
            command["user_id"],
            "No Oncall Services Defined",
            blocks=blocks,
        )
        return

    oncall_service_options = []
    for oncall_service in oncall_services:
        oncall_service_options.append(
            {"label": oncall_service.name, "value": oncall_service.external_id}
        )

    page_options = [{"label": "Yes", "value": "Yes"}, {"label": "No", "value": "No"}]

    dialog = {
        "callback_id": command["command"],
        "title": "Engage Oncall",
        "submit_label": "Engage",
        "elements": [
            {
                "label": "Oncall Service",
                "type": "select",
                "name": "oncall_service_id",
                "options": oncall_service_options,
            },
            {
                "label": "Page",
                "type": "select",
                "name": "page",
                "value": "No",
                "options": page_options,
            },
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@background_task
def create_status_report_dialog(incident_id: int, command: dict = None, db_session=None):
    """Fetches the last status report and creates a dialog."""
    # we load the most recent status report
    status_report = status_report_service.get_most_recent_by_incident_id(
        db_session=db_session, incident_id=incident_id
    )

    conditions = actions = needs = ""
    if status_report:
        conditions = status_report.conditions
        actions = status_report.actions
        needs = status_report.needs

    dialog = {
        "callback_id": command["command"],
        "title": "Status Report",
        "submit_label": "Submit",
        "elements": [
            {"type": "textarea", "label": "Conditions", "name": "conditions", "value": conditions},
            {"type": "textarea", "label": "Actions", "name": "actions", "value": actions},
            {"type": "textarea", "label": "Needs", "name": "needs", "value": needs},
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@background_task
def add_user_to_conversation(user_email: str, incident_id: int, action: dict, db_session=None):
    """Adds a user to a conversation."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    user_id = dispatch_slack_service.resolve_user(slack_client, user_email)["id"]

    dispatch_slack_service.add_users_to_conversation(
        slack_client, incident.conversation.channel_id, user_id
    )


def event_functions(event: EventEnvelope):
    """Interprets the events and routes it the appropriate function."""
    event_mappings = {
        "file_created": [add_evidence_to_storage],
        "file_shared": [add_evidence_to_storage],
        "link_shared": [],
        "member_joined_channel": [incident_flows.incident_add_or_reactivate_participant_flow],
        "message": [after_hours],
        "member_left_channel": [incident_flows.incident_remove_participant_flow],
        "message.groups": [],
        "message.im": [],
        "reaction_added": [add_message_to_timeline],
        "reaction_removed": [remove_message_from_timeline],
    }

    return event_mappings.get(event.event.type, [])


def command_functions(command: str):
    """Interprets the command and routes it the appropriate function."""
    command_mappings = {
        SLACK_COMMAND_ASSIGN_ROLE_SLUG: [create_assign_role_dialog],
        SLACK_COMMAND_UPDATE_INCIDENT_SLUG: [create_update_incident_dialog],
        SLACK_COMMAND_LIST_PARTICIPANTS_SLUG: [list_participants],
        SLACK_COMMAND_LIST_RESOURCES_SLUG: [incident_flows.incident_list_resources_flow],
        SLACK_COMMAND_LIST_TASKS_SLUG: [list_tasks],
        SLACK_COMMAND_MARK_ACTIVE_SLUG: [],
        SLACK_COMMAND_MARK_CLOSED_SLUG: [],
        SLACK_COMMAND_MARK_STABLE_SLUG: [],
        SLACK_COMMAND_STATUS_REPORT_SLUG: [create_status_report_dialog],
        SLACK_COMMAND_ENGAGE_ONCALL_SLUG: [create_engage_oncall_dialog],
    }

    return command_mappings.get(command, [])


@background_task
def handle_update_incident_action(user_email, incident_id, action, db_session=None):
    """Messages slack dialog data into something that Dispatch can use."""
    submission = action["submission"]
    notify = True if submission["notify"] == "Yes" else False
    incident_in = IncidentUpdate(
        title=submission["title"],
        description=submission["description"],
        incident_type={"name": submission["type"]},
        incident_priority={"name": submission["priority"]},
        status=submission["status"],
        visibility=submission["visibility"],
    )
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    existing_incident = IncidentRead.from_orm(incident)
    incident_service.update(db_session=db_session, incident=incident, incident_in=incident_in)
    incident_flows.incident_update_flow(user_email, incident_id, existing_incident, notify)


@background_task
def handle_assign_role_action(user_email, incident_id, action, db_session=None):
    """Messages slack dialog data into some thing that Dispatch can use."""
    assignee_user_id = action["submission"]["participant"]
    assignee_role = action["submission"]["role"]
    assignee_email = get_user_email(client=slack_client, user_id=assignee_user_id)
    incident_flows.incident_assign_role_flow(user_email, incident_id, assignee_email, assignee_role)


def action_functions(action: str):
    """Interprets the action and routes it the appropriate function."""
    action_mappings = {
        SLACK_COMMAND_STATUS_REPORT_SLUG: [status_report_flows.new_status_report_flow],
        SLACK_COMMAND_ASSIGN_ROLE_SLUG: [handle_assign_role_action],
        SLACK_COMMAND_UPDATE_INCIDENT_SLUG: [handle_update_incident_action],
        SLACK_COMMAND_ENGAGE_ONCALL_SLUG: [incident_flows.incident_engage_oncall_flow],
        ConversationButtonActions.invite_user: [add_user_to_conversation],
    }

    return action_mappings.get(action, [])


def get_action_name_by_action_type(action: dict):
    """Returns the action name based on the type."""
    action_name = ""
    if action["type"] == "dialog_submission":
        action_name = action["callback_id"]

    if action["type"] == "block_actions":
        action_name = action["actions"][0]["block_id"]

    return action_name


def get_incident_id_by_action_type(action: dict, db_session: SessionLocal):
    """Returns the incident id based on the action type."""
    incident_id = -1
    if action["type"] == "dialog_submission":
        channel_id = action["channel"]["id"]
        conversation = get_by_channel_id(db_session=db_session, channel_id=channel_id)
        incident_id = conversation.incident_id

    if action["type"] == "block_actions":
        incident_id = action["actions"][0]["value"]

    return incident_id


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

    if (
        event_body.type == "message" and event_body.subtype
    ):  # We ignore messages that have a subtype
        # Parse the Event payload and emit the event to the event listener
        response.headers["X-Slack-Powered-By"] = create_ua_string()
        return {"ok"}

    user_id = event_body.user

    # Fetch conversation by channel id
    channel_id = (  # We ensure channel_id always has a value
        event_body.channel_id if event_body.channel_id else event_body.channel
    )
    conversation = get_by_channel_id(db_session=db_session, channel_id=channel_id)

    if conversation and dispatch_slack_service.is_user(user_id):
        # We create an async Slack client
        slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

        # We resolve the user's email
        user_email = await dispatch_slack_service.get_user_email_async(slack_async_client, user_id)

        # Dispatch event functions to be executed in the background
        for f in event_functions(event):
            background_tasks.add_task(f, user_email, conversation.incident_id)

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
    command = request_body_form._dict

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # Fetch conversation by channel id
    channel_id = command.get("channel_id")
    conversation = get_by_channel_id(db_session=db_session, channel_id=channel_id)

    # Dispatch command functions to be executed in the background
    if conversation:
        for f in command_functions(command.get("command")):
            background_tasks.add_task(f, conversation.incident_id, command=command)

        return INCIDENT_CONVERSATION_COMMAND_MESSAGE.get(
            command.get("command"), f"Unable to find message. Command: {command.get('command')}"
        )
    else:
        return render_non_incident_conversation_command_error_message(command.get("command"))


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

    # We resolve the action name based on the type
    action_name = get_action_name_by_action_type(action)

    # we resolve the incident id based on the action type
    incident_id = get_incident_id_by_action_type(action, db_session)

    # Dispatch action functions to be executed in the background
    for f in action_functions(action_name):
        background_tasks.add_task(f, user_email, incident_id, action)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # When there are no exceptions within the dialog submission, your app must respond with 200 OK with an empty body.
    # This will complete the dialog. (https://api.slack.com/dialogs#validation)
    return {}
