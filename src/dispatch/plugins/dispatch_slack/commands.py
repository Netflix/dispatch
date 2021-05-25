import base64
import logging
from typing import List

from sqlalchemy.orm import Session

from dispatch.conversation import service as conversation_service
from dispatch.conversation.enums import ConversationButtonActions
from dispatch.database.core import resolve_attr
from dispatch.enums import Visibility
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.messaging import send_incident_resources_ephemeral_message_to_participant
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.project import service as project_service
from dispatch.task import service as task_service
from dispatch.task.models import TaskStatus, Task

from .config import (
    SLACK_APP_USER_SLUG,
    SLACK_COMMAND_ADD_TIMELINE_EVENT_SLUG,
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_LIST_INCIDENTS_SLUG,
    SLACK_COMMAND_LIST_MY_TASKS_SLUG,
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
    SLACK_COMMAND_LIST_RESOURCES_SLUG,
    SLACK_COMMAND_LIST_TASKS_SLUG,
    SLACK_COMMAND_REPORT_EXECUTIVE_SLUG,
    SLACK_COMMAND_REPORT_INCIDENT_SLUG,
    SLACK_COMMAND_REPORT_TACTICAL_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
    SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG,
    SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG,
    SLACK_COMMAND_RUN_WORKFLOW_SLUG,
    SLACK_COMMAND_LIST_WORKFLOWS_SLUG,
)

from .decorators import slack_background_task

from .dialogs import (
    create_assign_role_dialog,
    create_engage_oncall_dialog,
    create_executive_report_dialog,
    create_tactical_report_dialog,
)

from .messaging import (
    INCIDENT_CONVERSATION_COMMAND_MESSAGE,
    create_command_run_in_conversation_where_bot_not_present_message,
    create_command_run_in_nonincident_conversation_message,
    create_command_run_by_non_privileged_user_message,
)

from .modals.incident.handlers import (
    create_add_timeline_event_modal,
    create_report_incident_modal,
    create_update_incident_modal,
    create_update_notifications_group_modal,
    create_update_participant_modal,
)

from .modals.workflow.handlers import create_run_workflow_modal


log = logging.getLogger(__name__)


def base64_encode(input: str):
    """Returns a b64 encoded string."""
    return base64.b64encode(input.encode("ascii")).decode("ascii")


def check_command_restrictions(
    command: str, user_email: str, incident_id: int, db_session: Session
) -> bool:
    """Checks the current user's role to determine what commands they are allowed to run."""
    # some commands are sensitive and we only let non-participants execute them
    command_permissons = {
        SLACK_COMMAND_UPDATE_INCIDENT_SLUG: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.scribe,
        ],
        SLACK_COMMAND_ASSIGN_ROLE_SLUG: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.reporter,
            ParticipantRoleType.liaison,
            ParticipantRoleType.scribe,
        ],
        SLACK_COMMAND_REPORT_EXECUTIVE_SLUG: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.scribe,
        ],
        SLACK_COMMAND_REPORT_TACTICAL_SLUG: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.scribe,
        ],
    }

    # no permissions have been defined
    if command not in command_permissons.keys():
        return True

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # if any required role is active, allow command
    for active_role in participant.active_roles:
        for allowed_role in command_permissons[command]:
            if active_role.role == allowed_role:
                return True


def command_functions(command: str):
    """Interprets the command and routes it the appropriate function."""
    command_mappings = {
        SLACK_COMMAND_ADD_TIMELINE_EVENT_SLUG: [create_add_timeline_event_modal],
        SLACK_COMMAND_ASSIGN_ROLE_SLUG: [create_assign_role_dialog],
        SLACK_COMMAND_ENGAGE_ONCALL_SLUG: [create_engage_oncall_dialog],
        SLACK_COMMAND_LIST_INCIDENTS_SLUG: [list_incidents],
        SLACK_COMMAND_LIST_MY_TASKS_SLUG: [list_my_tasks],
        SLACK_COMMAND_LIST_PARTICIPANTS_SLUG: [list_participants],
        SLACK_COMMAND_LIST_RESOURCES_SLUG: [list_resources],
        SLACK_COMMAND_LIST_TASKS_SLUG: [list_tasks],
        SLACK_COMMAND_REPORT_EXECUTIVE_SLUG: [create_executive_report_dialog],
        SLACK_COMMAND_REPORT_INCIDENT_SLUG: [create_report_incident_modal],
        SLACK_COMMAND_REPORT_TACTICAL_SLUG: [create_tactical_report_dialog],
        SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG: [create_update_notifications_group_modal],
        SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG: [create_update_participant_modal],
        SLACK_COMMAND_UPDATE_INCIDENT_SLUG: [create_update_incident_modal],
        SLACK_COMMAND_RUN_WORKFLOW_SLUG: [create_run_workflow_modal],
        SLACK_COMMAND_LIST_WORKFLOWS_SLUG: [list_workflows],
    }

    return command_mappings.get(command, [])


def filter_tasks_by_assignee_and_creator(tasks: List[Task], by_assignee: str, by_creator: str):
    """Filters a list of tasks looking for a given creator or assignee."""
    filtered_tasks = []
    for t in tasks:
        if by_creator:
            creator_email = t.creator.individual.email
            if creator_email == by_creator:
                filtered_tasks.append(t)
                # lets avoid duplication if creator is also assignee
                continue

        if by_assignee:
            assignee_emails = [a.individual.email for a in t.assignees]
            if by_assignee in assignee_emails:
                filtered_tasks.append(t)

    return filtered_tasks


async def handle_slack_command(*, db_session, client, request, background_tasks):
    """Handles slack command message."""
    # We fetch conversation by channel id
    channel_id = request.get("channel_id")
    conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
        db_session=db_session, channel_id=channel_id
    )

    # We get the name of command that was run
    command = request.get("command")

    incident_id = 0
    if conversation:
        incident_id = conversation.incident_id
    else:
        if command not in [SLACK_COMMAND_REPORT_INCIDENT_SLUG, SLACK_COMMAND_LIST_INCIDENTS_SLUG]:
            # We let the user know that incident-specific commands
            # can only be run in incident conversations
            return create_command_run_in_nonincident_conversation_message(command)

        # We get the list of public and private conversations the Slack bot is a member of
        (
            public_conversations,
            private_conversations,
        ) = await dispatch_slack_service.get_conversations_by_user_id_async(
            client, SLACK_APP_USER_SLUG
        )

        # We get the name of conversation where the command was run
        conversation_id = request.get("channel_id")
        conversation_name = await dispatch_slack_service.get_conversation_name_by_id_async(
            client, conversation_id
        )

        if (
            not conversation_name
            or conversation_name not in public_conversations + private_conversations
        ):
            # We let the user know in which public conversations they can run the command
            return create_command_run_in_conversation_where_bot_not_present_message(
                command, public_conversations
            )

    user_id = request.get("user_id")
    user_email = await dispatch_slack_service.get_user_email_async(client, user_id)

    # some commands are sensitive and we only let non-participants execute them
    allowed = check_command_restrictions(
        command=command, user_email=user_email, incident_id=incident_id, db_session=db_session
    )
    if not allowed:
        return create_command_run_by_non_privileged_user_message(command)

    for f in command_functions(command):
        background_tasks.add_task(f, user_id, user_email, channel_id, incident_id, command=request)

    return INCIDENT_CONVERSATION_COMMAND_MESSAGE.get(command, f"Running... Command: {command}")


@slack_background_task
def list_resources(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Runs the list incident resources flow."""
    # we load the incident instance
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    # we send the list of resources to the participant
    send_incident_resources_ephemeral_message_to_participant(
        command["user_id"], incident, db_session
    )


@slack_background_task
def list_my_tasks(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Returns the list of incident tasks to the user as an ephemeral message."""
    list_tasks(
        user_id=user_id,
        user_email=user_email,
        channel_id=channel_id,
        incident_id=incident_id,
        command=command,
        by_creator=user_email,
        by_assignee=user_email,
        db_session=None,
        slack_client=None,
    )


@slack_background_task
def list_tasks(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
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
        button_text = "Resolve" if status.value == TaskStatus.open else "Re-open"
        action_type = "resolve" if status.value == TaskStatus.open else "reopen"

        tasks = task_service.get_all_by_incident_id_and_status(
            db_session=db_session, incident_id=incident_id, status=status.value
        )

        if by_creator or by_assignee:
            tasks = filter_tasks_by_assignee_and_creator(tasks, by_assignee, by_creator)

        for idx, task in enumerate(tasks):
            assignees = [f"<{a.individual.weblink}|{a.individual.name}>" for a in task.assignees]

            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*Description:* <{task.weblink}|{task.description}>\n"
                            f"*Creator:* <{task.creator.individual.weblink}|{task.creator.individual.name}>\n"
                            f"*Assignees:* {', '.join(assignees)}"
                        ),
                    },
                    "block_id": f"{ConversationButtonActions.update_task_status.value}-{task.status}-{idx}",
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": button_text},
                        "value": f"{action_type}-{base64_encode(task.resource_id)}",
                    },
                }
            )
        blocks.append({"type": "divider"})

    dispatch_slack_service.send_ephemeral_message(
        slack_client,
        channel_id,
        user_id,
        "Incident Task List",
        blocks=blocks,
    )


@slack_background_task
def list_workflows(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Returns the list of incident workflows to the user as an ephemeral message."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    blocks = []
    blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": "*Incident Workflows*"}})
    for w in incident.workflow_instances:
        artifact_links = ""
        for a in w.artifacts:
            artifact_links += f"- <{a.weblink}|{a.name}> \n"

        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Name:* <{w.weblink}|{w.workflow.name}>\n"
                        f"*Workflow Description:* {w.workflow.description}\n"
                        f"*Run Reason:* {w.run_reason}\n"
                        f"*Creator:* {w.creator.individual.name}\n"
                        f"*Status:* {w.status}\n"
                        f"*Artifacts:* \n {artifact_links}"
                    ),
                },
            }
        )
        blocks.append({"type": "divider"})

    dispatch_slack_service.send_ephemeral_message(
        slack_client,
        channel_id,
        user_id,
        "Incident Workflow List",
        blocks=blocks,
    )


@slack_background_task
def list_participants(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Returns the list of incident participants to the user as an ephemeral message."""
    blocks = []
    blocks.append(
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Incident Participants*"}}
    )

    participants = participant_service.get_all_by_incident_id(
        db_session=db_session, incident_id=incident_id
    ).all()

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    contact_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="contact"
    )

    for participant in participants:
        if participant.active_roles:
            participant_email = participant.individual.email
            participant_info = contact_plugin.instance.get(participant_email)
            participant_name = participant_info["fullname"]
            participant_team = participant_info["team"]
            participant_department = participant_info["department"]
            participant_location = participant_info["location"]
            participant_weblink = participant_info["weblink"]
            participant_avatar_url = dispatch_slack_service.get_user_avatar_url(
                slack_client, participant_email
            )

            participant_reason_added = participant.added_reason or "Unknown"
            if participant.added_by:
                participant_added_by = participant.added_by.individual.name
            else:
                participant_added_by = "Unknown"

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
                        f"*Reason Added*: {participant_reason_added}\n"
                        f"*Added By*: {participant_added_by}\n"
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
        channel_id,
        user_id,
        "Incident Participant List",
        blocks=blocks,
    )


@slack_background_task
def list_incidents(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Returns the list of current active and stable incidents,
    and closed incidents in the last 24 hours."""
    projects = []
    incidents = []

    # scopes reply to the current incident's project
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if incident:
        # command was run in an incident conversation
        projects.append(incident.project)
    else:
        # command was run in a non-incident conversation
        projects = project_service.get_all(db_session=db_session)

    for project in projects:
        # we fetch active incidents
        incidents.extend(
            incident_service.get_all_by_status(
                db_session=db_session, project_id=project.id, status=IncidentStatus.active.value
            )
        )
        # We fetch stable incidents
        incidents.extend(
            incident_service.get_all_by_status(
                db_session=db_session,
                project_id=project.id,
                status=IncidentStatus.stable.value,
            )
        )
        # We fetch closed incidents in the last 24 hours
        incidents.extend(
            incident_service.get_all_last_x_hours_by_status(
                db_session=db_session,
                project_id=project.id,
                status=IncidentStatus.closed.value,
                hours=24,
            )
        )

    blocks = []
    blocks.append({"type": "header", "text": {"type": "plain_text", "text": "List of Incidents"}})

    if incidents:
        for incident in incidents:
            if incident.visibility == Visibility.open.value:
                ticket_weblink = resolve_attr(incident, "ticket.weblink")
                try:
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": (
                                    f"*<{ticket_weblink}|{incident.name}>*\n"
                                    f"*Title*: {incident.title}\n"
                                    f"*Type*: {incident.incident_type.name}\n"
                                    f"*Priority*: {incident.incident_priority.name}\n"
                                    f"*Status*: {incident.status}\n"
                                    f"*Incident Commander*: <{incident.commander.individual.weblink}|{incident.commander.individual.name}>\n"
                                    f"*Project*: {incident.project.name}"
                                ),
                            },
                        }
                    )
                except Exception as e:
                    log.exception(e)

    dispatch_slack_service.send_ephemeral_message(
        slack_client,
        channel_id,
        user_id,
        "Incident List",
        blocks=blocks,
    )
