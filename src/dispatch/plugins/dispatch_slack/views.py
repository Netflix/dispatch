import arrow
import datetime
import hashlib
import hmac
import json
import logging
import platform
import sys

from time import time
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException

from pydantic import BaseModel

from sqlalchemy.orm import Session

from starlette.requests import Request
from starlette.responses import Response

from dispatch.config import INCIDENT_PLUGIN_CONTACT_SLUG, INCIDENT_PLUGIN_CONVERSATION_SLUG
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.conversation.service import get_by_channel_id
from dispatch.database import get_db, SessionLocal
from dispatch.decorators import background_task
from dispatch.enums import Visibility
from dispatch.event import service as event_service
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus, NewIncidentSubmission, IncidentSlackViewBlockId
from dispatch.incident.models import IncidentUpdate, IncidentRead
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.individual import service as individual_service
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.base import plugins
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.report import flows as report_flows
from dispatch.report import service as report_service
from dispatch.report.enums import ReportTypes
from dispatch.service import service as service_service
from dispatch.task import service as task_service
from dispatch.task.models import TaskStatus, Task

from . import __version__
from .config import (
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_EXECUTIVE_REPORT_SLUG,
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
    SLACK_COMMAND_LIST_RESOURCES_SLUG,
    SLACK_COMMAND_LIST_TASKS_SLUG,
    SLACK_COMMAND_LIST_MY_TASKS_SLUG,
    SLACK_COMMAND_REPORT_INCIDENT_SLUG,
    SLACK_COMMAND_TACTICAL_REPORT_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
    SLACK_SIGNING_SECRET,
    SLACK_TIMELINE_EVENT_REACTION,
    SLACK_BAN_THREADS,
)
from .messaging import (
    INCIDENT_CONVERSATION_COMMAND_MESSAGE,
    create_incident_reported_confirmation_msg,
    create_modal_content,
    render_non_incident_conversation_command_error_message,
)

from .service import get_user_email


router = APIRouter()
slack_client = dispatch_slack_service.create_slack_client()
log = logging.getLogger(__name__)


class SlackEventAppException(Exception):
    pass


class EventBodyItem(BaseModel):
    """Body item of the Slack event."""

    type: str = None
    channel: str = None
    ts: str = None


class EventBody(BaseModel):
    """Body of the Slack event."""

    channel: str = None
    channel_id: str = None
    channel_type: str = None
    deleted_ts: str = None
    event_ts: str = None
    thread_ts: str = None
    file_id: str = None
    hidden: bool = None
    inviter: str = None
    item: EventBodyItem = None
    item_user: str = None
    reaction: str = None
    subtype: str = None
    team: str = None
    text: str = None
    type: str
    user: str = None
    user_id: str = None


class EventEnvelope(BaseModel):
    """Envelope of the Slack event."""

    api_app_id: str = None
    authed_users: List[str] = []
    challenge: str = None
    enterprise_id: str = None
    event: EventBody = None
    event_id: str = None
    event_time: int = None
    team_id: str = None
    token: str = None
    type: str


@background_task
def handle_reaction_added_event(
    user_email: str, incident_id: int, event: dict = None, db_session=None
):
    """Handles an event where a reaction is added to a message."""
    reaction = event.event.reaction

    if reaction == SLACK_TIMELINE_EVENT_REACTION:
        conversation_id = event.event.item.channel
        message_ts = event.event.item.ts
        message_ts_utc = datetime.datetime.utcfromtimestamp(float(message_ts))

        # we fetch the message information
        response = dispatch_slack_service.list_conversation_messages(
            slack_client, conversation_id, latest=message_ts, limit=1, inclusive=1
        )
        message_text = response["messages"][0]["text"]
        message_sender_id = response["messages"][0]["user"]

        # we fetch the individual who sent the message
        message_sender_email = get_user_email(client=slack_client, user_id=message_sender_id)
        individual = individual_service.get_by_email(
            db_session=db_session, email=message_sender_email
        )

        convo_plugin = plugins.get(INCIDENT_PLUGIN_CONVERSATION_SLUG)

        # we log the event
        event_service.log(
            db_session=db_session,
            source=convo_plugin.title,
            description=f'"{message_text}," said {individual.name}',
            incident_id=incident_id,
            individual_id=individual.id,
            started_at=message_ts_utc,
        )


@background_task
def handle_reaction_removed_event(
    user_email: str, incident_id: int, event: dict = None, db_session=None
):
    """Handles an event where a reaction is removed from a message."""
    pass


@background_task
def add_evidence_to_storage(user_email: str, incident_id: int, event: dict = None, db_session=None):
    """Adds evidence (e.g. files) added/shared in the conversation to storage."""
    pass


def is_business_hours(commander_tz: str):
    """Determines if it's currently office hours where the incident commander is located."""
    now = arrow.utcnow().to(commander_tz)
    return now.weekday() not in [5, 6] and 9 <= now.hour < 17


@background_task
def after_hours(user_email: str, incident_id: int, event: dict = None, db_session=None):
    """Notifies the user that this incident is current in after hours mode."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

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
                            f"Responses may be delayed. The current incident priority is *{incident.incident_priority.name}*"
                            f" and your message was sent outside of the Incident Commander's working hours (Weekdays, 9am-5pm, {commander_tz} timezone)."
                        )
                    ),
                },
            }
        ]

        participant = participant_service.get_by_incident_id_and_email(
            incident_id=incident_id, email=user_email
        )
        if not participant.after_hours_notification:
            user_id = dispatch_slack_service.resolve_user(slack_client, user_email)["id"]
            dispatch_slack_service.send_ephemeral_message(
                slack_client, incident.conversation.channel_id, user_id, "", blocks=blocks
            )
            participant.after_hours_notification = True
            db_session.add(participant)
            db_session.commit()


def filter_tasks_by_assignee_and_creator(tasks: List[Task], by_assignee: str, by_creator: str):
    """Filters a list of tasks looking for a given creator or assignee."""
    filtered_tasks = []
    for t in tasks:
        if by_creator:
            creator_email = t.creator.individual.email
            if creator_email == by_creator:
                filtered_tasks.append(t)

        if by_assignee:
            assignee_emails = [a.individual.email for a in t.assignees]
            if by_assignee in assignee_emails:
                filtered_tasks.append(t)

    return filtered_tasks


@background_task
def list_my_tasks(incident_id: int, command: dict = None, db_session=None):
    """Returns the list of incident tasks to the user as an ephemeral message."""
    user_email = dispatch_slack_service.get_user_email(slack_client, command["user_id"])
    list_tasks(
        incident_id=incident_id,
        command=command,
        db_session=db_session,
        by_creator=user_email,
        by_assignee=user_email,
    )


@background_task
def list_tasks(
    incident_id: int,
    command: dict = None,
    db_session=None,
    by_creator: str = None,
    by_assignee: str = None,
):
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

        if by_creator or by_assignee:
            tasks = filter_tasks_by_assignee_and_creator(tasks, by_assignee, by_creator)

        for task in tasks:
            assignees = [a.individual.email for a in task.assignees]
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*Description:* <{task.weblink}|{task.description}>\n"
                            f"*Assignees:* {', '.join(assignees)}"
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
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Incident Participants*"}}
    )

    participants = participant_service.get_all_by_incident_id(
        db_session=db_session, incident_id=incident_id
    ).all()

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

            block = {
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
            }

            if len(participants) < 20:
                block.update(
                    {
                        "accessory": {
                            "type": "image",
                            "alt_text": participant_name,
                            "image_url": participant_avatar_url,
                        },
                    }
                )

            blocks.append(block)
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

    status_options = []
    for status in IncidentStatus:
        status_options.append({"label": status.value, "value": status.value})

    visibility_options = []
    for visibility in Visibility:
        visibility_options.append({"label": visibility.value, "value": visibility.value})

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
                "label": "Priority",
                "type": "select",
                "name": "priority",
                "value": incident.incident_priority.name,
                "options": priority_options,
            },
            {
                "label": "Status",
                "type": "select",
                "name": "status",
                "value": incident.status,
                "options": status_options,
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
                    "text": "No oncall services have been defined. You can define them in the Dispatch UI at /services",
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
def create_tactical_report_dialog(incident_id: int, command: dict = None, db_session=None):
    """Creates a dialog with the most recent tactical report data, if it exists."""
    # we load the most recent tactical report
    tactical_report = report_service.get_most_recent_by_incident_id_and_type(
        db_session=db_session, incident_id=incident_id, report_type=ReportTypes.tactical_report
    )

    conditions = actions = needs = ""
    if tactical_report:
        conditions = tactical_report.details.get("conditions")
        actions = tactical_report.details.get("actions")
        needs = tactical_report.details.get("needs")

    dialog = {
        "callback_id": command["command"],
        "title": "Tactical Report",
        "submit_label": "Submit",
        "elements": [
            {"type": "textarea", "label": "Conditions", "name": "conditions", "value": conditions},
            {"type": "textarea", "label": "Actions", "name": "actions", "value": actions},
            {"type": "textarea", "label": "Needs", "name": "needs", "value": needs},
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@background_task
def create_executive_report_dialog(incident_id: int, command: dict = None, db_session=None):
    """Creates a dialog with the most recent executive report data, if it exists."""
    # we load the most recent executive report
    executive_report = report_service.get_most_recent_by_incident_id_and_type(
        db_session=db_session, incident_id=incident_id, report_type=ReportTypes.executive_report
    )

    current_status = overview = next_steps = ""
    if executive_report:
        current_status = executive_report.details.get("current_status")
        overview = executive_report.details.get("overview")
        next_steps = executive_report.details.get("next_steps")

    dialog = {
        "callback_id": command["command"],
        "title": "Executive Report",
        "submit_label": "Submit",
        "elements": [
            {
                "type": "textarea",
                "label": "Current Status",
                "name": "current_status",
                "value": current_status,
            },
            {"type": "textarea", "label": "Overview", "name": "overview", "value": overview},
            {"type": "textarea", "label": "Next Steps", "name": "next_steps", "value": next_steps},
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@background_task
def add_user_to_conversation(
    user_id: str, user_email: str, incident_id: int, action: dict, db_session=None
):
    """Adds a user to a conversation."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if incident.status == IncidentStatus.closed:
        message = f"Sorry, we cannot add you to a closed incident. Please reach out to the incident commander ({incident.commander.name}) for details."
        dispatch_slack_service.send_ephemeral_message(
            slack_client, action["container"]["channel_id"], user_id, message
        )
    else:
        dispatch_slack_service.add_users_to_conversation(
            slack_client, incident.conversation.channel_id, [user_id]
        )
        message = f"Success! We've added you to incident {incident.name}. Please check your side bar for the new channel."
        dispatch_slack_service.send_ephemeral_message(
            slack_client, action["container"]["channel_id"], user_id, message
        )


@background_task
def ban_threads_warning(user_email: str, incident_id: int, event: dict = None, db_session=None):
    """Sends the user an ephemeral message if they use threads."""
    if not SLACK_BAN_THREADS:
        return

    if event.event.thread_ts:
        # we should be able to look for `subtype == message_replied` once this bug is fixed
        # https://api.slack.com/events/message/message_replied
        # From Slack: Bug alert! This event is missing the subtype field when dispatched
        # over the Events API. Until it is fixed, examine message events' thread_ts value.
        # When present, it's a reply. To be doubly sure, compare a thread_ts to the top-level ts
        # value, when they differ the latter is a reply to the former.
        message = "Please refrain from using threads in incident related channels. Threads make it harder for incident participants to maintain context."
        dispatch_slack_service.send_ephemeral_message(
            slack_client,
            event.event.channel,
            event.event.user,
            message,
            thread_ts=event.event.thread_ts,
        )


def event_functions(event: EventEnvelope):
    """Interprets the events and routes it the appropriate function."""
    event_mappings = {
        "file_created": [add_evidence_to_storage],
        "file_shared": [add_evidence_to_storage],
        "link_shared": [],
        "member_joined_channel": [incident_flows.incident_add_or_reactivate_participant_flow],
        "message": [ban_threads_warning],
        "member_left_channel": [incident_flows.incident_remove_participant_flow],
        "message.groups": [],
        "message.im": [],
        "reaction_added": [handle_reaction_added_event],
        "reaction_removed": [handle_reaction_removed_event],
    }

    return event_mappings.get(event.event.type, [])


def command_functions(command: str):
    """Interprets the command and routes it the appropriate function."""
    command_mappings = {
        SLACK_COMMAND_ASSIGN_ROLE_SLUG: [create_assign_role_dialog],
        SLACK_COMMAND_ENGAGE_ONCALL_SLUG: [create_engage_oncall_dialog],
        SLACK_COMMAND_EXECUTIVE_REPORT_SLUG: [create_executive_report_dialog],
        SLACK_COMMAND_LIST_PARTICIPANTS_SLUG: [list_participants],
        SLACK_COMMAND_LIST_RESOURCES_SLUG: [incident_flows.incident_list_resources_flow],
        SLACK_COMMAND_LIST_TASKS_SLUG: [list_tasks],
        SLACK_COMMAND_LIST_MY_TASKS_SLUG: [list_my_tasks],
        SLACK_COMMAND_TACTICAL_REPORT_SLUG: [create_tactical_report_dialog],
        SLACK_COMMAND_UPDATE_INCIDENT_SLUG: [create_update_incident_dialog],
    }

    return command_mappings.get(command, [])


@background_task
def handle_update_incident_action(user_id, user_email, incident_id, action, db_session=None):
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
def handle_assign_role_action(user_id, user_email, incident_id, action, db_session=None):
    """Messages slack dialog data into some thing that Dispatch can use."""
    assignee_user_id = action["submission"]["participant"]
    assignee_role = action["submission"]["role"]
    assignee_email = get_user_email(client=slack_client, user_id=assignee_user_id)
    incident_flows.incident_assign_role_flow(user_email, incident_id, assignee_email, assignee_role)


def action_functions(action: str):
    """Interprets the action and routes it the appropriate function."""
    action_mappings = {
        ConversationButtonActions.invite_user: [add_user_to_conversation],
        NewIncidentSubmission.form_slack_view: [report_incident_from_submitted_form],
        SLACK_COMMAND_ASSIGN_ROLE_SLUG: [handle_assign_role_action],
        SLACK_COMMAND_ENGAGE_ONCALL_SLUG: [incident_flows.incident_engage_oncall_flow],
        SLACK_COMMAND_EXECUTIVE_REPORT_SLUG: [report_flows.create_executive_report],
        SLACK_COMMAND_TACTICAL_REPORT_SLUG: [report_flows.create_tactical_report],
        SLACK_COMMAND_UPDATE_INCIDENT_SLUG: [handle_update_incident_action],
    }

    # this allows for unique action blocks e.g. invite-user or invite-user-1, etc
    for key in action_mappings.keys():
        if key in action:
            return action_mappings[key]
    return []


def get_action_name_by_action_type(action: dict):
    """Returns the action name based on the type."""
    action_name = ""
    if action["type"] == "dialog_submission":
        action_name = action["callback_id"]

    if action["type"] == "block_actions":
        action_name = action["actions"][0]["block_id"]

    # TODO: maybe use callback info in the future to differentiate action types
    if action["type"] == "view_submission":
        action_name = NewIncidentSubmission.form_slack_view

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


def get_channel_id(event_body: dict):
    """Returns the channel id from the Slack event."""
    channel_id = ""
    if event_body.channel_id:
        return event_body.channel_id
    if event_body.channel:
        return event_body.channel
    if event_body.item.channel:
        return event_body.item.channel

    return channel_id


@background_task
def create_report_incident_modal(command: dict = None, db_session=None):
    """
    Prepare the Modal / View x
    Ask slack to open a modal with the prepared Modal / View content
    """
    channel_id = command.get("channel_id")
    trigger_id = command.get("trigger_id")

    type_options = []
    for t in incident_type_service.get_all(db_session=db_session):
        type_options.append({"label": t.name, "value": t.name})

    priority_options = []
    for priority in incident_priority_service.get_all(db_session=db_session):
        priority_options.append({"label": priority.name, "value": priority.name})

    modal_view_template = create_modal_content(
        channel_id=channel_id, incident_types=type_options, incident_priorities=priority_options
    )

    dispatch_slack_service.open_modal_with_user(
        client=slack_client, trigger_id=trigger_id, modal=modal_view_template
    )


def parse_submitted_form(view_data: dict):
    """Parse the submitted data and return important / required fields for Dispatch to create an incident."""
    parsed_data = {}
    state_elem = view_data.get("state")
    state_values = state_elem.get("values")
    for state in state_values:
        state_key_value_pair = state_values[state]

        for elem_key in state_key_value_pair:
            elem_key_value_pair = state_values[state][elem_key]

            if elem_key_value_pair.get("selected_option") and elem_key_value_pair.get(
                "selected_option"
            ).get("value"):
                parsed_data[state] = {
                    "name": elem_key_value_pair.get("selected_option").get("text").get("text"),
                    "value": elem_key_value_pair.get("selected_option").get("value"),
                }
            else:
                parsed_data[state] = elem_key_value_pair.get("value")

    return parsed_data


@background_task
def report_incident_from_submitted_form(
    user_id: str,
    user_email: str,
    incident_id: int,
    action: dict,
    db_session: Session = Depends(get_db),
):
    submitted_form = action.get("view")

    # Fetch channel id from private metadata field
    channel_id = submitted_form.get("private_metadata")

    parsed_form_data = parse_submitted_form(submitted_form)

    requested_form_title = parsed_form_data.get(IncidentSlackViewBlockId.title)
    requested_form_description = parsed_form_data.get(IncidentSlackViewBlockId.description)
    requested_form_incident_type = parsed_form_data.get(IncidentSlackViewBlockId.type)
    requested_form_incident_priority = parsed_form_data.get(IncidentSlackViewBlockId.priority)

    # send a confirmation to the user
    msg_template = create_incident_reported_confirmation_msg(
        title=requested_form_title,
        incident_type=requested_form_incident_type.get("value"),
        incident_priority=requested_form_incident_priority.get("value"),
    )

    dispatch_slack_service.send_ephemeral_message(
        client=slack_client,
        conversation_id=channel_id,
        user_id=user_id,
        text="",
        blocks=msg_template,
    )

    # create the incident
    incident = incident_service.create(
        db_session=db_session,
        title=requested_form_title,
        status=IncidentStatus.active,
        description=requested_form_description,
        incident_type=requested_form_incident_type,
        incident_priority=requested_form_incident_priority,
        reporter_email=user_email,
    )

    incident_flows.incident_create_flow(incident_id=incident.id)


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
    channel_id = get_channel_id(event_body)
    conversation = get_by_channel_id(db_session=db_session, channel_id=channel_id)

    if conversation and dispatch_slack_service.is_user(user_id):
        # We create an async Slack client
        slack_async_client = dispatch_slack_service.create_slack_client(run_async=True)

        # We resolve the user's email
        user_email = await dispatch_slack_service.get_user_email_async(slack_async_client, user_id)

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
    command = request_body_form._dict

    # We verify the timestamp
    verify_timestamp(x_slack_request_timestamp)

    # We verify the signature
    verify_signature(raw_request_body, x_slack_request_timestamp, x_slack_signature)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # If the incoming slash command is equal to reporting new incident slug
    if command.get("command") == SLACK_COMMAND_REPORT_INCIDENT_SLUG:
        background_tasks.add_task(
            func=create_report_incident_modal, db_session=db_session, command=command
        )

        return INCIDENT_CONVERSATION_COMMAND_MESSAGE.get(
            command.get("command"), f"Unable to find message. Command: {command.get('command')}"
        )
    else:
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

    # if the request was made as a form submission from slack then we skip getting the incident_id
    # the incident will be created in in the next step
    incident_id = 0
    if action_name != NewIncidentSubmission.form_slack_view:
        # we resolve the incident id based on the action type
        incident_id = get_incident_id_by_action_type(action, db_session)

    # Dispatch action functions to be executed in the background
    for f in action_functions(action_name):
        background_tasks.add_task(f, user_id, user_email, incident_id, action)

    # We add the user-agent string to the response headers
    response.headers["X-Slack-Powered-By"] = create_ua_string()

    # When there are no exceptions within the dialog submission, your app must respond with 200 OK with an empty body.
    response_body = {}
    if action_name == NewIncidentSubmission.form_slack_view:
        # For modals we set "response_action" to "clear" to close all views in the modal.
        # An empty body is currently not working.
        response_body = {"response_action": "clear"}

    return response_body
