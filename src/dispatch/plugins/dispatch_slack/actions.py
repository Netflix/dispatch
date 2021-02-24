import base64
from fastapi import BackgroundTasks

from dispatch.conversation import service as conversation_service
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.conversation.messaging import send_feedack_to_user
from dispatch.database import SessionLocal
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import IncidentUpdate, IncidentRead
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.report import flows as report_flows
from dispatch.report.models import ExecutiveReportCreate, TacticalReportCreate
from dispatch.task import service as task_service
from dispatch.task.models import TaskStatus

from .config import (
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_REPORT_EXECUTIVE_SLUG,
    SLACK_COMMAND_REPORT_TACTICAL_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
)

from .modals import create_rating_feedback_modal, handle_modal_action
from .service import get_user_email
from .decorators import slack_background_task


def base64_decode(input: str):
    """Returns a b64 decoded string."""
    return base64.b64decode(input.encode("ascii")).decode("ascii")

async def handle_slack_action(*, db_session, client, request, background_tasks):
    """Handles slack action message."""
    # We resolve the user's email
    user_id = request["user"]["id"]
    user_email = await dispatch_slack_service.get_user_email_async(client, user_id)

    request["user"]["email"] = user_email

    # When there are no exceptions within the dialog submission, your app must respond with 200 OK with an empty body.
    response_body = {}
    if request.get("view"):
        handle_modal_action(request, background_tasks)
        if request["type"] == "view_submission":
            # For modals we set "response_action" to "clear" to close all views in the modal.
            # An empty body is currently not working.
            response_body = {"response_action": "clear"}
    elif request["type"] == "dialog_submission":
        handle_dialog_action(request, background_tasks, db_session=db_session)
    elif request["type"] == "block_actions":
        handle_block_action(request, background_tasks)

    return response_body


@slack_background_task
def add_user_to_conversation(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Adds a user to a conversation."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    if not incident:
        message = "Sorry, we cannot add you to this incident it does not exist."
        dispatch_slack_service.send_ephemeral_message(slack_client, channel_id, user_id, message)
    elif incident.status == IncidentStatus.closed:
        message = f"Sorry, we cannot add you to a closed incident. Please reach out to the incident commander ({incident.commander.individual.name}) for details."
        dispatch_slack_service.send_ephemeral_message(slack_client, channel_id, user_id, message)
    else:
        dispatch_slack_service.add_users_to_conversation(
            slack_client, incident.conversation.channel_id, [user_id]
        )
        message = f"Success! We've added you to incident {incident.name}. Please check your side bar for the new channel."
        dispatch_slack_service.send_ephemeral_message(slack_client, channel_id, user_id, message)


@slack_background_task
def update_task_status(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Updates a task based on user input."""
    action_type, external_task_id_b64 = action["actions"][0]["value"].split("-")
    external_task_id = base64_decode(external_task_id_b64)

    resolve = True
    if action_type == "reopen":
        resolve = False

    # we only update the external task allowing syncing to care of propagation to dispatch
    task = task_service.get_by_resource_id(db_session=db_session, resource_id=external_task_id)

    # avoid external calls if we are already in the desired state
    if resolve and task.status == TaskStatus.resolved:
        message = "Task is already resolved."
        dispatch_slack_service.send_ephemeral_message(slack_client, channel_id, user_id, message)
        return

    if not resolve and task.status == TaskStatus.open:
        message = "Task is already open."
        dispatch_slack_service.send_ephemeral_message(slack_client, channel_id, user_id, message)
        return

    # we don't currently have a good way to get the correct file_id (we don't store a task <-> relationship)
    # lets try in both the incident doc and PIR doc
    drive_task_plugin = plugin_service.get_active(db_session=db_session, plugin_type="task")

    try:
        file_id = task.incident.incident_document.resource_id
        drive_task_plugin.instance.update(file_id, external_task_id, resolved=resolve)
    except Exception:
        file_id = task.incident.incident_review_document.resource_id
        drive_task_plugin.instance.update(file_id, external_task_id, resolved=resolve)

    status = "resolved" if task.status == TaskStatus.open else "re-opened"
    message = f"Task successfully {status}."
    dispatch_slack_service.send_ephemeral_message(slack_client, channel_id, user_id, message)


@slack_background_task
def handle_update_incident_action(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Massages slack dialog data into something that Dispatch can use."""
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


@slack_background_task
def handle_engage_oncall_action(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Adds and pages based on the oncall modal."""
    oncall_service_id = action["submission"]["oncall_service_id"]
    page = action["submission"]["page"]

    oncall_individual, oncall_service = incident_flows.incident_engage_oncall_flow(
        user_email, incident_id, oncall_service_id, page=page, db_session=db_session
    )

    if not oncall_service or not oncall_individual:
        message = "Could not engage oncall. Oncall service plugin not enabled."
    else:
        message = f"You have successfully engaged {oncall_individual.name} from oncall rotation {oncall_service.name}."
    dispatch_slack_service.send_ephemeral_message(slack_client, channel_id, user_id, message)


@slack_background_task
def handle_tactical_report_create(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Handles the creation of a tactical report."""
    tactical_report_in = TacticalReportCreate(
        conditions=action["submission"]["conditions"],
        actions=action["submission"]["actions"],
        needs=action["submission"]["needs"],
    )
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    report_flows.create_tactical_report(
        user_email=user_email,
        incident_id=incident_id,
        tactical_report_in=tactical_report_in,
        db_session=db_session,
    )

    # we let the user know that the report has been sent to the tactical group
    send_feedack_to_user(
        incident.conversation.channel_id,
        user_id,
        f"The tactical report has been emailed to the incident tactical group ({incident.tactical_group.email}).",
        db_session,
    )


@slack_background_task
def handle_executive_report_create(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Handles the creation of executive reports."""
    executive_report_in = ExecutiveReportCreate(
        current_status=action["submission"]["current_status"],
        overview=action["submission"]["overview"],
        next_steps=action["submission"]["next_steps"],
    )
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    executive_report = report_flows.create_executive_report(
        user_email=user_email,
        incident_id=incident_id,
        executive_report_in=executive_report_in,
        db_session=db_session,
    )

    # we let the user know that the report has been created
    send_feedack_to_user(
        incident.conversation.channel_id,
        user_id,
        f"The executive report document has been created and can be found in the incident storage here: {executive_report.document.weblink}",
        db_session,
    )

    # we let the user know that the report has been sent to the notifications group
    send_feedack_to_user(
        incident.conversation.channel_id,
        user_id,
        f"The executive report has been emailed to the incident notifications group ({incident.notifications_group.email}).",
        db_session,
    )


@slack_background_task
def handle_assign_role_action(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Massages slack dialog data into something that Dispatch can use."""
    assignee_user_id = action["submission"]["participant"]
    assignee_role = action["submission"]["role"]
    assignee_email = get_user_email(client=slack_client, user_id=assignee_user_id)
    incident_flows.incident_assign_role_flow(user_email, incident_id, assignee_email, assignee_role)


def dialog_action_functions(action: str):
    """Interprets the action and routes it to the appropriate function."""
    action_mappings = {
        SLACK_COMMAND_ASSIGN_ROLE_SLUG: [handle_assign_role_action],
        SLACK_COMMAND_ENGAGE_ONCALL_SLUG: [handle_engage_oncall_action],
        SLACK_COMMAND_REPORT_EXECUTIVE_SLUG: [handle_executive_report_create],
        SLACK_COMMAND_REPORT_TACTICAL_SLUG: [handle_tactical_report_create],
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
        ConversationButtonActions.invite_user.value: [add_user_to_conversation],
        ConversationButtonActions.provide_feedback.value: [create_rating_feedback_modal],
        ConversationButtonActions.update_task_status.value: [update_task_status],
        # Note these are temporary for backward compatibility of block ids and should be remove in a future release
        "ConversationButtonActions.invite_user": [add_user_to_conversation],
        "ConversationButtonActions.provide_feedback": [create_rating_feedback_modal],
        "ConversationButtonActions.update_task_status": [
            update_task_status,
        ],
    }

    # this allows for unique action blocks e.g. invite-user or invite-user-1, etc
    for key in action_mappings.keys():
        if key in action:
            return action_mappings[key]
    return []


def handle_dialog_action(action: dict, background_tasks: BackgroundTasks, db_session: SessionLocal):
    """Handles all dialog actions."""
    channel_id = action["channel"]["id"]
    conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
        db_session=db_session, channel_id=channel_id
    )
    incident_id = conversation.incident_id

    user_id = action["user"]["id"]
    user_email = action["user"]["email"]

    action_id = action["callback_id"]

    for f in dialog_action_functions(action_id):
        background_tasks.add_task(f, user_id, user_email, channel_id, incident_id, action)


def handle_block_action(action: dict, background_tasks: BackgroundTasks):
    """Handles a standalone block action."""

    action_id = action["actions"][0]["block_id"]
    incident_id = action["actions"][0]["value"]
    user_id = action["user"]["id"]
    user_email = action["user"]["email"]
    channel_id = action["container"]["channel_id"]

    for f in block_action_functions(action_id):
        background_tasks.add_task(f, user_id, user_email, channel_id, incident_id, action)
