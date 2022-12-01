import base64
import logging
from typing import List
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic import BaseModel

from sqlalchemy.orm import Session

from dispatch.exceptions import NotFoundError

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
from dispatch.plugins.dispatch_slack.models import TaskButton
from dispatch.project import service as project_service
from dispatch.task import service as task_service
from dispatch.task.enums import TaskStatus
from dispatch.task.models import Task

from .config import SlackConfiguration, SlackConversationConfiguration

from .decorators import (
    get_organization_scope_from_channel_id,
    slack_background_task,
)

from .dialogs import (
    create_assign_role_dialog,
    create_engage_oncall_dialog,
    create_executive_report_dialog,
    create_tactical_report_dialog,
)

from .messaging import (
    get_incident_conversation_command_message,
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
    config: SlackConfiguration, command: str, user_email: str, incident_id: int, db_session: Session
) -> bool:
    """Checks the current user's role to determine what commands they are allowed to run."""
    # some commands are sensitive and we only let non-participants execute them
    command_permissions = {
        config.slack_command_add_timeline_event: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.scribe,
        ],
        config.slack_command_assign_role: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.liaison,
            ParticipantRoleType.scribe,
            ParticipantRoleType.reporter,
            ParticipantRoleType.participant,
            ParticipantRoleType.observer,
        ],
        config.slack_command_report_executive: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.scribe,
        ],
        config.slack_command_report_tactical: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.scribe,
        ],
        config.slack_command_update_incident: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.scribe,
        ],
        config.slack_command_update_notifications_group: [
            ParticipantRoleType.incident_commander,
            ParticipantRoleType.scribe,
        ],
    }

    # no permissions have been defined
    if command not in command_permissions.keys():
        return True

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    # if any required role is active, allow command
    for active_role in participant.active_roles:
        for allowed_role in command_permissions[command]:
            if active_role.role == allowed_role:
                return True


def command_functions(config: SlackConfiguration, command: str):
    """Interprets the command and routes it the appropriate function."""
    command_mappings = {
        config.slack_command_add_timeline_event: [create_add_timeline_event_modal],
        config.slack_command_assign_role: [create_assign_role_dialog],
        config.slack_command_engage_oncall: [create_engage_oncall_dialog],
        config.slack_command_list_incidents: [list_incidents],
        config.slack_command_list_my_tasks: [list_my_tasks],
        config.slack_command_list_participants: [list_participants],
        config.slack_command_list_resources: [list_resources],
        config.slack_command_list_tasks: [list_tasks],
        config.slack_command_list_workflows: [list_workflows],
        config.slack_command_report_executive: [create_executive_report_dialog],
        config.slack_command_report_incident: [create_report_incident_modal],
        config.slack_command_report_tactical: [create_tactical_report_dialog],
        config.slack_command_run_workflow: [create_run_workflow_modal],
        config.slack_command_update_incident: [create_update_incident_modal],
        config.slack_command_update_notifications_group: [create_update_notifications_group_modal],
        config.slack_command_update_participant: [create_update_participant_modal],
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


async def handle_non_incident_conversation_commands(config, client, request, background_tasks):
    """Handles all commands that do not have a specific incident conversation."""
    command = request.get("command")
    channel_id = request.get("channel_id")
    command_args = request.get("text", "").split(" ")
    if command_args:
        organization_slug = command_args[0]

    # We get the list of public and private conversations the Dispatch bot is a member of
    (
        public_conversations,
        private_conversations,
    ) = await dispatch_slack_service.get_conversations_by_user_id_async(
        client, config.app_user_slug
    )

    # We get the name of conversation where the command was run
    conversation_name = await dispatch_slack_service.get_conversation_name_by_id_async(
        client, channel_id
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

    for f in command_functions(config, command):
        background_tasks.add_task(
            f,
            user_id=user_id,
            user_email=user_email,
            channel_id=channel_id,
            config=config,
            incident_id=None,
            organization_slug=organization_slug,
            command=request,
        )

    return get_incident_conversation_command_message(config, command)


async def handle_incident_conversation_commands(config, client, request, background_tasks):
    """Handles all commands that are issued from an incident conversation."""
    channel_id = request.get("channel_id")
    command = request.get("command")
    db_session = get_organization_scope_from_channel_id(channel_id=channel_id)

    if not db_session:
        # We let the user know that incident-specific commands
        # can only be run in incident conversations
        return create_command_run_in_nonincident_conversation_message(command)

    conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
        db_session=db_session, channel_id=channel_id
    )

    user_id = request.get("user_id")
    user_email = await dispatch_slack_service.get_user_email_async(client, user_id)

    # some commands are sensitive and we only let non-participants execute them
    allowed = check_command_restrictions(
        config=config,
        command=command,
        user_email=user_email,
        incident_id=conversation.incident.id,
        db_session=db_session,
    )
    if not allowed:
        return create_command_run_by_non_privileged_user_message(command)

    for f in command_functions(config, command):
        background_tasks.add_task(
            f,
            user_id=user_id,
            user_email=user_email,
            channel_id=channel_id,
            config=config,
            incident_id=conversation.incident.id,
            command=request,
        )

    db_session.close()

    return get_incident_conversation_command_message(config, command)


async def handle_slack_command(*, config, client, request, background_tasks):
    """Handles slack command message."""
    # We get the name of command that was run
    command = request.get("command")
    if command in [config.slack_command_report_incident, config.slack_command_list_incidents]:
        return await handle_non_incident_conversation_commands(
            config, client, request, background_tasks
        )
    else:
        return await handle_incident_conversation_commands(
            config, client, request, background_tasks
        )


@slack_background_task
def list_resources(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    config: SlackConversationConfiguration = None,
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
    config: SlackConversationConfiguration = None,
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
        config=config,
        command=command,
        by_creator=user_email,
        by_assignee=user_email,
        db_session=db_session,
        slack_client=slack_client,
    )


@slack_background_task
def list_tasks(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    config: SlackConversationConfiguration = None,
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
                "text": {"type": "mrkdwn", "text": f"*{status} Incident Tasks*"},
            }
        )
        button_text = "Resolve" if status == TaskStatus.open else "Re-open"
        action_type = "resolve" if status == TaskStatus.open else "reopen"

        tasks = task_service.get_all_by_incident_id_and_status(
            db_session=db_session, incident_id=incident_id, status=status
        )

        if by_creator or by_assignee:
            tasks = filter_tasks_by_assignee_and_creator(tasks, by_assignee, by_creator)

        for idx, task in enumerate(tasks):
            assignees = [f"<{a.individual.weblink}|{a.individual.name}>" for a in task.assignees]

            task_button = TaskButton(
                organization_slug=task.project.organization.slug,
                action_type=action_type,
                incident_id=incident_id,
                resource_id=task.resource_id,
            )

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
                    "block_id": f"{ConversationButtonActions.update_task_status}-{task.status}-{idx}",
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": button_text},
                        "value": task_button.json(),
                        "action_id": f"{ConversationButtonActions.update_task_status}",
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
    config: SlackConversationConfiguration = None,
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
    config: SlackConversationConfiguration = None,
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
            participant_info = contact_plugin.instance.get(participant_email, db_session=db_session)
            participant_name = participant_info.get("fullname", participant.individual.email)
            participant_team = participant_info.get("team", "Unknown")
            participant_department = participant_info.get("department", "Unknown")
            participant_location = participant_info.get("location", "Unknown")
            participant_weblink = participant_info.get("weblink")
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

            # TODO we should make this more resilient to missing data (kglisson)
            block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Name:* <{participant_weblink}|{participant_name} ({participant_email})>\n"
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
    config: SlackConversationConfiguration = None,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Returns the list of current active and stable incidents,
    and closed incidents in the last 24 hours."""
    projects = []
    incidents = []
    args = command["text"].split(" ")

    # scopes reply to the current incident's project
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if incident:
        # command was run in an incident conversation
        projects.append(incident.project)
    else:
        # command was run in a non-incident conversation
        if len(args) == 2:
            project = project_service.get_by_name(db_session=db_session, name=args[1])

            if project:
                projects.append()
            else:
                raise ValidationError(
                    [
                        ErrorWrapper(
                            NotFoundError(
                                msg=f"Project name '{args[1]}' in organization '{args[0]}' not found. Check your spelling."
                            ),
                            loc="project",
                        )
                    ],
                    model=BaseModel,
                )

        else:
            projects = project_service.get_all(db_session=db_session)

    for project in projects:
        # we fetch active incidents
        incidents.extend(
            incident_service.get_all_by_status(
                db_session=db_session, project_id=project.id, status=IncidentStatus.active
            )
        )
        # We fetch stable incidents
        incidents.extend(
            incident_service.get_all_by_status(
                db_session=db_session,
                project_id=project.id,
                status=IncidentStatus.stable,
            )
        )
        # We fetch closed incidents in the last 24 hours
        incidents.extend(
            incident_service.get_all_last_x_hours_by_status(
                db_session=db_session,
                project_id=project.id,
                status=IncidentStatus.closed,
                hours=24,
            )
        )

    blocks = []
    blocks.append({"type": "header", "text": {"type": "plain_text", "text": "List of Incidents"}})

    if incidents:
        for incident in incidents:
            if incident.visibility == Visibility.open:
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
                                    f"*Severity*: {incident.incident_severity.name}\n"
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
