from typing import List

from dispatch.config import INCIDENT_PLUGIN_CONTACT_SLUG

from dispatch.decorators import background_task
from dispatch.incident import flows as incident_flows
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.plugins.base import plugins
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.task import service as task_service
from dispatch.task.models import TaskStatus, Task
from dispatch.conversation.enums import ConversationButtonActions

from .config import (
    SLACK_COMMAND_ASSIGN_ROLE_SLUG,
    SLACK_COMMAND_ENGAGE_ONCALL_SLUG,
    SLACK_COMMAND_EXECUTIVE_REPORT_SLUG,
    SLACK_COMMAND_LIST_MY_TASKS_SLUG,
    SLACK_COMMAND_LIST_PARTICIPANTS_SLUG,
    SLACK_COMMAND_LIST_RESOURCES_SLUG,
    SLACK_COMMAND_LIST_TASKS_SLUG,
    SLACK_COMMAND_REPORT_INCIDENT_SLUG,
    SLACK_COMMAND_TACTICAL_REPORT_SLUG,
    SLACK_COMMAND_UPDATE_INCIDENT_SLUG,
    SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG,
    SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG,
)

from .modals import (
    create_update_notifications_group_modal,
    create_report_incident_modal,
    create_update_participant_modal,
)

from .dialogs import (
    create_assign_role_dialog,
    create_engage_oncall_dialog,
    create_executive_report_dialog,
    create_tactical_report_dialog,
    create_update_incident_dialog,
)

slack_client = dispatch_slack_service.create_slack_client()


def command_functions(command: str):
    """Interprets the command and routes it the appropriate function."""
    command_mappings = {
        SLACK_COMMAND_ASSIGN_ROLE_SLUG: [create_assign_role_dialog],
        SLACK_COMMAND_ENGAGE_ONCALL_SLUG: [create_engage_oncall_dialog],
        SLACK_COMMAND_EXECUTIVE_REPORT_SLUG: [create_executive_report_dialog],
        SLACK_COMMAND_LIST_MY_TASKS_SLUG: [list_my_tasks],
        SLACK_COMMAND_LIST_PARTICIPANTS_SLUG: [list_participants],
        SLACK_COMMAND_LIST_RESOURCES_SLUG: [incident_flows.incident_list_resources_flow],
        SLACK_COMMAND_LIST_TASKS_SLUG: [list_tasks],
        SLACK_COMMAND_REPORT_INCIDENT_SLUG: [create_report_incident_modal],
        SLACK_COMMAND_TACTICAL_REPORT_SLUG: [create_tactical_report_dialog],
        SLACK_COMMAND_UPDATE_INCIDENT_SLUG: [create_update_incident_dialog],
        SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG: [create_update_notifications_group_modal],
        SLACK_COMMAND_UPDATE_PARTICIPANT_SLUG: [create_update_participant_modal],
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
                    "block_id": f"{ConversationButtonActions.update_task_status}-{task.status}-{idx}",
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": button_text},
                        "value": f"{action_type}-{task.resource_id}",
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
        command["channel_id"],
        command["user_id"],
        "Incident List Participants",
        blocks=blocks,
    )
