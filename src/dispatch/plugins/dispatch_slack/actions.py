from fastapi import BackgroundTasks

from dispatch.incident.enums import IncidentStatus
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.conversation.service import get_by_channel_id
from dispatch.database import SessionLocal
from dispatch.decorators import background_task
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.models import IncidentUpdate, IncidentRead
from dispatch.report import flows as report_flows
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service

from .config import (
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_EXECUTIVE_REPORT_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
    SLACK_COMMAND_TACTICAL_REPORT_SLUG,
)

from .service import get_user_email

slack_client = dispatch_slack_service.create_slack_client()


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


def dialog_action_functions(action: str):
    """Interprets the action and routes it to the appropriate function."""
    action_mappings = {
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


def block_action_functions(action: str):
    """Interprets the action and routes it to the appropriate function."""
    action_mappings = {
        ConversationButtonActions.invite_user: [add_user_to_conversation],
    }

    # this allows for unique action blocks e.g. invite-user or invite-user-1, etc
    for key in action_mappings.keys():
        if key in action:
            return action_mappings[key]
    return []


def handle_dialog_action(action: dict, background_tasks: BackgroundTasks, db_session: SessionLocal):
    """Handles all dialog actions."""
    channel_id = action["channel"]["id"]
    conversation = get_by_channel_id(db_session=db_session, channel_id=channel_id)
    incident_id = conversation.incident_id

    user_id = action["user"]["id"]
    user_email = action["user"]["email"]

    action_id = action["callback_id"]

    for f in dialog_action_functions(action_id):
        background_tasks.add_task(f, user_id, user_email, incident_id, action)


def handle_block_action(action: dict, background_tasks: BackgroundTasks):
    """Handles a standalone block action."""

    action_id = action["actions"][0]["block_id"]
    incident_id = action["actions"][0]["value"]
    user_id = action["user"]["id"]
    user_email = action["user"]["email"]

    for f in block_action_functions(action_id):
        background_tasks.add_task(f, user_id, user_email, incident_id, action)
