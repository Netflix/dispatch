import logging
import re
import uuid
from functools import partial
from datetime import datetime, timedelta
from typing import Any

import pytz
from blockkit import (
    Actions,
    Button,
    Checkboxes,
    Context,
    Divider,
    Image,
    Input,
    MarkdownText,
    Message,
    Modal,
    PlainOption,
    PlainTextInput,
    Section,
    UsersSelect,
)
from slack_bolt import Ack, BoltContext, BoltRequest, Respond
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.case import service as case_service
from dispatch.case import flows as case_flows
from dispatch.config import DISPATCH_UI_URL
from dispatch.database.service import search_filter_sort_paginate
from dispatch.enums import Visibility, EventType, SubjectNames
from dispatch.event import service as event_service
from dispatch.exceptions import DispatchException
from dispatch.group import flows as group_flows
from dispatch.group.enums import GroupAction
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import IncidentCreate, IncidentRead, IncidentUpdate
from dispatch.individual import service as individual_service
from dispatch.individual.models import IndividualContactRead
from dispatch.monitor import service as monitor_service
from dispatch.monitor.models import MonitorCreate
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantUpdate
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.enums import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.decorators import message_dispatcher
from dispatch.plugins.dispatch_slack.enums import SlackAPIErrorCode
from dispatch.plugins.dispatch_slack.exceptions import CommandError, EventError
from dispatch.plugins.dispatch_slack.fields import (
    DefaultActionIds,
    DefaultBlockIds,
    TimezoneOptions,
    datetime_picker_block,
    description_input,
    incident_priority_select,
    incident_severity_select,
    incident_status_select,
    incident_type_select,
    participant_select,
    project_select,
    resolution_input,
    static_select_block,
    tag_multi_select,
    title_input,
)
from dispatch.plugins.dispatch_slack.incident.enums import (
    AddTimelineEventActions,
    AssignRoleActions,
    AssignRoleBlockIds,
    EngageOncallActionIds,
    EngageOncallActions,
    EngageOncallBlockIds,
    IncidentNotificationActions,
    IncidentReportActions,
    IncidentUpdateActions,
    IncidentShortcutCallbacks,
    LinkMonitorActionIds,
    LinkMonitorBlockIds,
    RemindAgainActions,
    ReportExecutiveActions,
    ReportExecutiveBlockIds,
    ReportTacticalActions,
    ReportTacticalBlockIds,
    TaskNotificationActionIds,
    UpdateNotificationGroupActionIds,
    UpdateNotificationGroupActions,
    UpdateNotificationGroupBlockIds,
    UpdateParticipantActions,
    UpdateParticipantBlockIds,
)
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    button_context_middleware,
    command_context_middleware,
    configuration_middleware,
    db_middleware,
    is_bot,
    message_context_middleware,
    modal_submit_middleware,
    reaction_context_middleware,
    restricted_command_middleware,
    subject_middleware,
    user_middleware,
    select_context_middleware,
    shortcut_context_middleware,
)
from dispatch.plugins.dispatch_slack.modals.common import send_success_modal
from dispatch.plugins.dispatch_slack.models import (
    MonitorMetadata,
    TaskMetadata,
    IncidentSubjects,
    CaseSubjects,
)
from dispatch.plugins.dispatch_slack.service import (
    get_user_email,
    get_user_profile_by_email,
)
from dispatch.project import service as project_service
from dispatch.report import flows as report_flows
from dispatch.report import service as report_service
from dispatch.report.enums import ReportTypes
from dispatch.report.models import ExecutiveReportCreate, TacticalReportCreate
from dispatch.service import service as service_service
from dispatch.tag import service as tag_service
from dispatch.task import service as task_service
from dispatch.task.enums import TaskStatus
from dispatch.task.models import Task
from dispatch.ticket import flows as ticket_flows
from dispatch.messaging.strings import reminder_select_values
from dispatch.plugins.dispatch_slack.messaging import build_unexpected_error_message

log = logging.getLogger(__file__)


def is_target_reaction(reaction: str) -> bool:
    """Returns True if given reaction matches the events' reaction."""

    def is_target(event) -> bool:
        return event["reaction"] == reaction

    return is_target


def configure(config):
    """Maps commands/events to their functions."""
    incident_command_context_middleware = partial(
        command_context_middleware,
        expected_subject=SubjectNames.INCIDENT,
    )

    middleware = [
        subject_middleware,
        configuration_middleware,
    ]

    # don't need an incident context
    app.command(config.slack_command_report_incident, middleware=middleware)(
        handle_report_incident_command
    )
    app.command(config.slack_command_list_incidents, middleware=middleware)(
        handle_list_incidents_command
    )

    # non-sensitive-commands
    middleware = [
        subject_middleware,
        configuration_middleware,
        incident_command_context_middleware,
    ]

    app.command(config.slack_command_list_tasks, middleware=middleware)(handle_list_tasks_command)
    app.command(config.slack_command_list_my_tasks, middleware=middleware)(
        handle_list_tasks_command
    )
    app.command(config.slack_command_list_participants, middleware=middleware)(
        handle_list_participants_command
    )
    app.command(config.slack_command_update_participant, middleware=middleware)(
        handle_update_participant_command
    )
    app.command(config.slack_command_engage_oncall, middleware=middleware)(
        handle_engage_oncall_command
    )

    # sensitive commands
    middleware = [
        subject_middleware,
        configuration_middleware,
        incident_command_context_middleware,
        user_middleware,
        restricted_command_middleware,
    ]

    app.command(config.slack_command_assign_role, middleware=middleware)(handle_assign_role_command)
    app.command(config.slack_command_update_incident, middleware=middleware)(
        handle_update_incident_command
    )
    app.command(config.slack_command_update_notifications_group, middleware=middleware)(
        handle_update_notifications_group_command
    )
    app.command(config.slack_command_report_tactical, middleware=middleware)(
        handle_report_tactical_command
    )
    app.command(config.slack_command_report_executive, middleware=middleware)(
        handle_report_executive_command
    )
    app.command(config.slack_command_add_timeline_event, middleware=middleware)(
        handle_add_timeline_event_command
    )

    app.event(
        event="reaction_added",
        matchers=[is_target_reaction(config.timeline_event_reaction)],
        middleware=[reaction_context_middleware],
    )(handle_timeline_added_event)

    app.event(
        event="reaction_added",
        middleware=[reaction_context_middleware],
    )(handle_not_configured_reaction_event)


@app.options(
    DefaultActionIds.tags_multi_select, middleware=[action_context_middleware, db_middleware]
)
def handle_tag_search_action(
    ack: Ack, payload: dict, context: BoltContext, db_session: Session
) -> None:
    """Handles tag lookup actions."""
    query_str = payload["value"]

    filter_spec = {
        "and": [
            {"model": "Project", "op": "==", "field": "id", "value": context["subject"].project_id}
        ]
    }

    if "/" in query_str:
        tag_type, query_str = query_str.split("/")
        filter_spec["and"].append(
            {"model": "TagType", "op": "==", "field": "name", "value": tag_type}
        )

    tags = search_filter_sort_paginate(
        db_session=db_session, model="Tag", query_str=query_str, filter_spec=filter_spec
    )

    options = []
    for t in tags["items"]:
        options.append(
            {
                "text": {"type": "plain_text", "text": f"{t.tag_type.name}/{t.name}"},
                "value": str(t.id),  # NOTE: slack doesn't accept int's as values (fails silently)
            }
        )

    ack(options=options)


@app.action(
    IncidentUpdateActions.project_select, middleware=[action_context_middleware, db_middleware]
)
def handle_update_incident_project_select_action(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    ack()
    values = body["view"]["state"]["values"]

    project_id = values[DefaultBlockIds.project_select][IncidentUpdateActions.project_select][
        "selected_option"
    ]["value"]

    context["subject"].project_id = project_id

    project = project_service.get(
        db_session=db_session,
        project_id=project_id,
    )

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    blocks = [
        Context(elements=[MarkdownText(text="Use this form to update the incident's details.")]),
        title_input(initial_value=incident.title),
        description_input(initial_value=incident.description),
        resolution_input(initial_value=incident.resolution),
        incident_status_select(initial_option={"text": incident.status, "value": incident.status}),
        project_select(
            db_session=db_session,
            initial_option={"text": project.name, "value": project.id},
            action_id=IncidentUpdateActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(
            db_session=db_session,
            initial_option={
                "text": incident.incident_type.name,
                "value": incident.incident_type.id,
            },
            project_id=project.id,
        ),
        incident_severity_select(
            db_session=db_session,
            initial_option={
                "text": incident.incident_severity.name,
                "value": incident.incident_severity.id,
            },
            project_id=project.id,
        ),
        incident_priority_select(
            db_session=db_session,
            initial_option={
                "text": incident.incident_priority.name,
                "value": incident.incident_priority.id,
            },
            project_id=project.id,
        ),
        tag_multi_select(
            optional=True,
            initial_options=[t.name for t in incident.tags],
        ),
    ]
    modal = Modal(
        title="Update Incident",
        blocks=blocks,
        submit="Update",
        close="Cancel",
        callback_id=IncidentUpdateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


# COMMANDS
def handle_list_incidents_command(
    ack: Ack,
    body: dict,
    payload: dict,
    db_session: Session,
    context: BoltContext,
    client: WebClient,
) -> None:
    """Handles the list incidents command."""
    ack()

    projects = []

    if context["subject"].type == IncidentSubjects.incident:
        # command was run in an incident conversation
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        projects.append(incident.project)
    else:
        # command was run in a non-incident conversation
        args = payload["command"].split(" ")

        if len(args) == 2:
            project = project_service.get_by_name(db_session=db_session, name=args[1])

            if project:
                projects.append(project)
            else:
                raise CommandError(
                    f"Project name '{args[1]}' in organization '{args[0]}' not found. Check your spelling.",
                )
        else:
            projects = project_service.get_all(db_session=db_session)

    incidents = []
    for project in projects:
        # We fetch active incidents
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

    if incidents:
        open_incidents = [i for i in incidents if i.visibility == Visibility.open]
        if len(open_incidents) > 50:
            blocks.extend(
                [
                    Context(
                        elements=[
                            "💡 There are more than 50 open incidents, which is the max we can display."
                        ]
                    ),
                    Divider(),
                ]
            )

        for idx, incident in enumerate(open_incidents[0:49], 1):
            incident_weblink = f"{DISPATCH_UI_URL}/{incident.project.organization.name}/incidents/{incident.name}?project={incident.project.name}"
            blocks.extend(
                [
                    Section(
                        fields=[
                            f"*<{incident_weblink}|{incident.name}>*\n {incident.title}",
                            f"*Commander*\n<{incident.commander.individual.weblink}|{incident.commander.individual.name}>",
                            f"*Project*\n{incident.project.name}",
                            f"*Status*\n{incident.status}",
                            f"*Type*\n {incident.incident_type.name}",
                            f"*Severity*\n {incident.incident_severity.name}",
                            f"*Priority*\n {incident.incident_priority.name}",
                        ]
                    )
                ]
            )
            # Don't add a divider if we are at the last incident
            if idx != len(open_incidents):
                blocks.extend([Divider()])

    modal = Modal(
        title="Incident List",
        blocks=blocks,
        close="Close",
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def handle_list_participants_command(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    """Handles list participants command."""
    ack()
    blocks = []

    participants = participant_service.get_all_by_incident_id(
        db_session=db_session, incident_id=context["subject"].id
    ).all()

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    contact_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="contact"
    )
    if not contact_plugin:
        raise CommandError(
            "Contact plugin is not enabled. Unable to list participants.",
        )

    active_participants = [p for p in participants if p.active_roles]
    for idx, participant in enumerate(active_participants, 1):
        participant_email = participant.individual.email
        participant_info = contact_plugin.instance.get(participant_email, db_session=db_session)
        participant_name = participant_info.get("fullname", participant.individual.email)
        participant_team = participant_info.get("team", "Unknown")
        participant_department = participant_info.get("department", "Unknown")
        participant_location = participant_info.get("location", "Unknown")
        participant_weblink = participant_info.get("weblink")

        participant_active_roles = participant_role_service.get_all_active_roles(
            db_session=db_session, participant_id=participant.id
        )
        participant_roles = []
        for role in participant_active_roles:
            participant_roles.append(role.role)

        accessory = None
        # don't load avatars for large incidents
        if len(participants) < 20:
            participant_avatar_url = dispatch_slack_service.get_user_avatar_url(
                client, participant_email
            )
            accessory = Image(image_url=participant_avatar_url, alt_text=participant_name)

        blocks.extend(
            [
                Section(
                    fields=[
                        f"*Name* \n<{participant_weblink}|{participant_name}>",
                        f"*Team*\n {participant_team}, {participant_department}",
                        f"*Location* \n{participant_location}",
                        f"*Incident Role(s)* \n{(', ').join(participant_roles)}",
                        (
                            f"*Added By* \n{participant.added_by.individual.name}"
                            if participant.added_by
                            else "*Added By* \nUnknown"
                        ),
                        (
                            f"*Added Reason* \n{participant.added_reason}"
                            if participant.added_reason
                            else "*Added Reason* \nUnknown"
                        ),
                    ],
                    accessory=accessory,
                ),
            ]
        )

        # Don't add a divider if we are at the last participant
        if idx != len(active_participants):
            blocks.extend([Divider()])

    modal = Modal(
        title="Incident Participants",
        blocks=blocks,
        close="Close",
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def filter_tasks_by_assignee_and_creator(
    tasks: list[Task], by_assignee: str, by_creator: str
) -> list[Task]:
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


def handle_list_tasks_command(
    ack: Ack,
    body: dict,
    payload: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    """Handles the list tasks command."""
    ack()

    tasks = task_service.get_all_by_incident_id(
        db_session=db_session,
        incident_id=context["subject"].id,
    )

    caller_only = False
    email = None
    if body["command"] == context["config"].slack_command_list_my_tasks:
        caller_only = True

    if caller_only:
        email = (client.users_info(user=payload["user_id"]))["user"]["profile"]["email"]
        tasks = filter_tasks_by_assignee_and_creator(tasks, email, email)

    draw_task_modal(
        channel_id=context.channel_id,
        client=client,
        first_open=True,
        tasks=tasks,
        view_id=body["trigger_id"],
    )


def draw_task_modal(
    channel_id: str,
    client: WebClient,
    first_open: bool,
    tasks: list[Task],
    view_id: str,
) -> None:
    """Builds and draws the list tasks modal on first open and after each button click."""
    blocks = []

    for status in TaskStatus:
        blocks.append(Section(text=f"*{status} Incident Tasks*"))
        button_text = "Resolve" if status == TaskStatus.open else "Re-open"
        action_type = "resolve" if status == TaskStatus.open else "reopen"

        tasks_for_status = [task for task in tasks if task.status == status]

        if not tasks_for_status:
            blocks.append(Section(text="No tasks."))

        for idx, task in enumerate(tasks_for_status, 1):
            assignees = [f"<{a.individual.weblink}|{a.individual.name}>" for a in task.assignees]

            button_metadata = TaskMetadata(
                type=IncidentSubjects.incident,
                action_type=action_type,
                organization_slug=task.project.organization.slug,
                id=task.incident.id,
                task_id=task.id,
                project_id=task.project.id,
                resource_id=task.resource_id,
                channel_id=channel_id,
            ).json()

            blocks.append(
                Section(
                    fields=[
                        (
                            f"*Description:* \n <{task.weblink}|{task.description}>"
                            if task.weblink
                            else f"*Description:* \n {task.description}"
                        ),
                        f"*Creator:* \n <{task.creator.individual.weblink}|{task.creator.individual.name}>",
                        f"*Assignees:* \n {', '.join(assignees)}",
                    ],
                    accessory=Button(
                        text=button_text,
                        value=button_metadata,
                        action_id=TaskNotificationActionIds.update_status,
                    ),
                )
            )
            # Don't add a divider if we are at the last task
            if idx != len(tasks_for_status):
                blocks.extend([Divider()])

    modal = Modal(
        title="Incident Tasks",
        blocks=blocks,
        close="Close",
    ).build()

    if first_open is True:
        client.views_open(trigger_id=view_id, view=modal)
    else:
        client.views_update(view_id=view_id, view=modal)


# EVENTS


def handle_not_configured_reaction_event(
    ack: Ack, client: Any, context: BoltContext, payload: Any, db_session: Session
) -> None:
    """Ignores reaction_added events for reactions that are not configured and mapped to a handler function."""
    ack()


def get_user_name_from_id(client: Any, user_id: str) -> str:
    """Returns the user's name given their user ID."""
    try:
        user = client.users_info(user=user_id)
        return user["user"]["profile"]["real_name"]
    except SlackApiError:
        # if can't find user, just return the original text
        return user_id


def replace_slack_users_in_message(client: Any, message: str) -> str:
    """Replaces slack user ids in a message with their names."""
    return re.sub(r"<@([^>]+)>", lambda x: f"@{get_user_name_from_id(client, x.group(1))}", message)


def handle_timeline_added_event(
    ack: Ack, client: Any, context: BoltContext, payload: Any, db_session: Session
) -> None:
    """Handles an event where the configured timeline reaction is added to a message."""
    ack()

    conversation_id = context["channel_id"]
    message_ts = payload["item"]["ts"]
    message_ts_utc = datetime.utcfromtimestamp(float(message_ts))

    # we fetch the message information
    response = dispatch_slack_service.list_conversation_messages(
        client, conversation_id, latest=message_ts, limit=1, inclusive=1
    )
    message_text = replace_slack_users_in_message(client, response["messages"][0]["text"])
    message_sender_id = response["messages"][0]["user"]

    # TODO: (wshel) handle case reactions
    if context["subject"].type == IncidentSubjects.incident:
        # we fetch the incident
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

        # we fetch the individual who sent the message
        # if user is not found, we default to "Unknown"
        try:
            message_sender_email = get_user_email(client=client, user_id=message_sender_id)
            individual = individual_service.get_by_email_and_project(
                db_session=db_session, email=message_sender_email, project_id=incident.project.id
            )
        except Exception:
            individual = None

        source = "Slack message"
        # if the individual is not found, see if it is a bot
        if individual is None:
            if bot_user_id := context["bot_user_id"]:
                try:
                    bot = dispatch_slack_service.get_user_info_by_id(client, bot_user_id)
                    bot_name = bot["profile"]["real_name"]
                    source = f"Slack message from {bot_name}"
                except Exception:
                    pass
        else:
            source = f"Slack message from {individual.name}"

        # we log the event
        event_service.log_incident_event(
            db_session=db_session,
            source=source,
            description=message_text,
            incident_id=context["subject"].id,
            individual_id=individual.id if individual else None,
            started_at=message_ts_utc,
            type=EventType.imported_message,
            owner=individual.name if individual else None,
        )


@message_dispatcher.add(
    subject=IncidentSubjects.incident, exclude={"subtype": ["channel_join", "channel_leave"]}
)  # we ignore channel join and leave messages
def handle_participant_role_activity(
    ack: Ack, db_session: Session, context: BoltContext, user: DispatchUser
) -> None:
    """
    Increments the participant role's activity counter and assesses the need of changing
    a participant's role based on its activity and changes it if needed.
    """
    ack()
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=context["subject"].id, email=user.email
    )

    if participant:
        for participant_role in participant.active_roles:
            participant_role.activity += 1

            # re-assign role once threshold is reached
            if participant_role.role == ParticipantRoleType.observer:
                if participant_role.activity >= 10:  # ten messages sent to the incident channel
                    # we change the participant's role to the participant one
                    participant_role_service.renounce_role(
                        db_session=db_session, participant_role=participant_role
                    )
                    participant_role_service.add_role(
                        db_session=db_session,
                        participant_id=participant.id,
                        participant_role=ParticipantRoleType.participant,
                    )

                    # we log the event
                    event_service.log_incident_event(
                        db_session=db_session,
                        source="Slack Plugin - Conversation Management",
                        description=(
                            f"{participant.individual.name}'s role changed from {participant_role.role} to "
                            f"{ParticipantRoleType.participant} due to activity in the incident channel"
                        ),
                        incident_id=context["subject"].id,
                        type=EventType.participant_updated,
                    )

            db_session.commit()


@message_dispatcher.add(
    subject=IncidentSubjects.incident, exclude={"subtype": ["channel_join", "group_join"]}
)  # we ignore user channel and group join messages
def handle_after_hours_message(
    ack: Ack,
    context: BoltContext,
    client: WebClient,
    db_session: Session,
    payload: dict,
    user: DispatchUser,
) -> None:
    """Notifies the user that this incident is currently in after hours mode."""
    ack()

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
    owner_email = incident.commander.individual.email
    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=context["subject"].id, email=user.email
    )
    # handle no participant found
    if not participant:
        return

    # get their timezone from slack
    try:
        owner_tz = (dispatch_slack_service.get_user_info_by_email(client, email=owner_email))["tz"]
    except SlackApiError as e:
        if e.response["error"] == SlackAPIErrorCode.USERS_NOT_FOUND:
            e.add_note(
                "This error usually indicates that the incident commanders Slack account is deactivated."
            )

        log.warning(f"Failed to fetch timezone from Slack API: {e}")
        owner_tz = (
            "UTC"  # set a default timezone value (change this to your preferred default timezone)
        )

    message = f"Responses may be delayed. The current incident priority is *{incident.incident_priority.name}* and your message was sent outside of the Incident Commander's working hours (Weekdays, 9am-5pm, {owner_tz} timezone)."

    now = datetime.now(pytz.timezone(owner_tz))
    is_business_hours = now.weekday() not in [5, 6] and 9 <= now.hour < 17

    if not is_business_hours:
        if not participant.after_hours_notification:
            participant.after_hours_notification = True
            db_session.add(participant)
            db_session.commit()
            client.chat_postEphemeral(
                text=message,
                channel=payload["channel"],
                user=payload["user"],
            )


@message_dispatcher.add(subject=IncidentSubjects.incident)
def handle_thread_creation(
    ack: Ack, client: WebClient, payload: dict, context: BoltContext, request: BoltRequest
) -> None:
    """Sends the user an ephemeral message if they use threads."""
    ack()

    if not context["config"].ban_threads:
        return

    if payload.get("thread_ts") and not is_bot(request):
        message = "Please refrain from using threads in incident channels. Threads make it harder for incident participants to maintain context."
        client.chat_postEphemeral(
            text=message,
            channel=payload["channel"],
            thread_ts=payload["thread_ts"],
            user=payload["user"],
        )


@message_dispatcher.add(subject=IncidentSubjects.incident)
def handle_message_monitor(
    ack: Ack,
    payload: dict,
    context: BoltContext,
    client: WebClient,
    db_session: Session,
) -> None:
    """Looks for strings that are available for monitoring (e.g. links)."""
    ack()

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
    project_id = incident.project.id

    plugins = plugin_service.get_active_instances(
        db_session=db_session, project_id=project_id, plugin_type="monitor"
    )

    for p in plugins:
        for matcher in p.instance.get_matchers():
            for match in matcher.finditer(payload["text"]):
                match_data = match.groupdict()
                monitor = monitor_service.get_by_weblink(
                    db_session=db_session, weblink=match_data["weblink"]
                )

                # silence ignored matches
                if monitor:
                    continue

                current_status = p.instance.get_match_status(match_data)
                if current_status:
                    status_text = ""
                    for k, v in current_status.items():
                        status_text += f"*{k.title()}*:\n{v.title()}\n"

                    button_metadata = MonitorMetadata(
                        type=IncidentSubjects.incident,
                        organization_slug=incident.project.organization.slug,
                        id=incident.id,
                        plugin_instance_id=p.id,
                        project_id=incident.project.id,
                        channel_id=context["channel_id"],
                        weblink=match_data["weblink"],
                    ).json()

                    blocks = [
                        Section(
                            text=f"Hi! Dispatch is able to monitor the status of the following resource: \n {match_data['weblink']} \n\n Would you like to be notified about changes in its status in the incident channel?"
                        ),
                        Section(text=status_text),
                        Actions(
                            block_id=LinkMonitorBlockIds.monitor,
                            elements=[
                                Button(
                                    text="Monitor",
                                    action_id=LinkMonitorActionIds.monitor,
                                    style="primary",
                                    value=button_metadata,
                                ),
                                Button(
                                    text="Ignore",
                                    action_id=LinkMonitorActionIds.ignore,
                                    style="primary",
                                    value=button_metadata,
                                ),
                            ],
                        ),
                    ]
                    blocks = Message(blocks=blocks).build()["blocks"]
                    client.chat_postEphemeral(
                        text="Link Monitor",
                        channel=payload["channel"],
                        thread_ts=payload.get("thread_ts"),
                        blocks=blocks,
                        user=payload["user"],
                    )


@app.event(
    "member_joined_channel",
    middleware=[
        message_context_middleware,
        user_middleware,
        configuration_middleware,
    ],
)
def handle_member_joined_channel(
    ack: Ack,
    user: DispatchUser,
    body: dict,
    client: WebClient,
    db_session: Session,
    context: BoltContext,
) -> None:
    """Handles the member_joined_channel Slack event."""
    ack()

    if not user:
        raise EventError(
            "Unable to handle member_joined_channel Slack event. Dispatch user unknown."
        )

    if context["subject"].type == IncidentSubjects.incident:
        participant = incident_flows.incident_add_or_reactivate_participant_flow(
            user_email=user.email, incident_id=context["subject"].id, db_session=db_session
        )

        if not participant:
            # Participant is already in the incident channel.
            return

        participant.user_conversation_id = context["user_id"]

        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

        # If the user was invited, the message will include an inviter property containing the user ID of the inviting user.
        # The property will be absent when a user manually joins a channel, or a user is added by default (e.g. #general channel).
        inviter = body.get("event", {}).get("inviter", None)
        inviter_is_user = (
            dispatch_slack_service.is_user(context["config"], inviter) if inviter else None
        )

        if inviter and inviter_is_user:
            # Participant is added into the incident channel using an @ message or /invite command.
            inviter_email = get_user_email(client=client, user_id=inviter)
            added_by_participant = participant_service.get_by_incident_id_and_email(
                db_session=db_session, incident_id=context["subject"].id, email=inviter_email
            )
            participant.added_by = added_by_participant

        else:
            # User joins via the `join` button on Web Application or Slack.
            # We default to the incident commander when we don't know who added the user or the user is the Dispatch bot.
            incident = incident_service.get(
                db_session=db_session, incident_id=context["subject"].id
            )
            participant.added_by = incident.commander

        # Message text when someone @'s a user is not available in body, use generic added by reason
        participant.added_reason = f"Participant added by {participant.added_by.individual.name}"

        db_session.add(participant)
        db_session.commit()

    if context["subject"].type == CaseSubjects.case:
        case = case_service.get(db_session=db_session, case_id=context["subject"].id)

        if not case.dedicated_channel:
            return

        participant = case_flows.case_add_or_reactivate_participant_flow(
            user_email=user.email,
            case_id=context["subject"].id,
            db_session=db_session,
        )

        if not participant:
            # Participant is already in the case channel.
            return

        participant.user_conversation_id = context["user_id"]

        # If the user was invited, the message will include an inviter property containing the user ID of the inviting user.
        # The property will be absent when a user manually joins a channel, or a user is added by default (e.g. #general channel).
        inviter = body.get("event", {}).get("inviter", None)
        inviter_is_user = (
            dispatch_slack_service.is_user(context["config"], inviter) if inviter else None
        )

        if inviter and inviter_is_user:
            # Participant is added into the incident channel using an @ message or /invite command.
            inviter_email = get_user_email(client=client, user_id=inviter)
            added_by_participant = participant_service.get_by_case_id_and_email(
                db_session=db_session,
                case_id=context["subject"].id,
                email=inviter_email,
            )
            participant.added_by = added_by_participant

        else:
            # User joins via the `join` button on Web Application or Slack.
            # We default to the incident commander when we don't know who added the user or the user is the Dispatch bot.
            participant.added_by = case.assignee

        # Message text when someone @'s a user is not available in body, use generic added by reason
        participant.added_reason = f"Participant added by {participant.added_by.individual.name}"

        db_session.add(participant)
        db_session.commit()


@app.event(
    "member_left_channel",
    middleware=[
        message_context_middleware,
        user_middleware,
    ],
)
def handle_member_left_channel(
    ack: Ack, context: BoltContext, db_session: Session, user: DispatchUser
) -> None:
    ack()

    if context["subject"].type == IncidentSubjects.incident:
        incident_flows.incident_remove_participant_flow(
            user.email, context["subject"].id, db_session=db_session
        )

    if context["subject"].type == CaseSubjects.case:
        case = case_service.get(db_session=db_session, case_id=context["subject"].id)

        if not case.dedicated_channel:
            return

        case_flows.case_remove_participant_flow(
            user_email=user.email,
            case_id=context["subject"].id,
            db_session=db_session,
        )


# MODALS


def handle_add_timeline_event_command(
    ack: Ack, body: dict, client: WebClient, context: BoltContext
) -> None:
    """Handles the add timeline event command."""
    ack()
    description = None
    date = ""
    time = ""
    if re.match(".*DESC\\s*(.+?)(?: DATE|$|TIME)", body["text"], re.IGNORECASE):
        description = (
            re.match("DESC\\s*(.+?)(?: DATE|$|TIME)", body["text"], re.IGNORECASE).group(1)
        ).strip()
    if re.match(
        ".*DATE\\s*(\\d{4}\\-\\d{2}\\-\\d{2})(?: TIME|$|DESC)", body["text"], re.IGNORECASE
    ):
        date = (
            re.match(
                ".*DATE\\s*(\\d{4}\\-\\d{2}\\-\\d{2})(?: TIME|$|DESC)", body["text"], re.IGNORECASE
            ).group(1)
        ).strip()
    if re.match(
        ".*TIME\\s*(([01]?[0-9]|2[0-3]):[0-5][0-9])(?: |DATE|$|DESC)", body["text"], re.IGNORECASE
    ):
        time = (
            re.match(
                ".*TIME\\s*(([01]?[0-9]|2[0-3]):[0-5][0-9])(?: |DATE|$|DESC)",
                body["text"],
                re.IGNORECASE,
            ).group(1)
        ).strip()

    blocks = [
        Context(
            elements=[
                MarkdownText(text="Use this form to add an event to the incident's timeline.")
            ]
        ),
        description_input(initial_value=description),
    ]

    blocks.extend(datetime_picker_block(initial_option=date + "|" + time))

    modal = Modal(
        title="Add Timeline Event",
        blocks=blocks,
        submit="Add",
        close="Close",
        callback_id=AddTimelineEventActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_add_timeline_submission_event(ack: Ack) -> None:
    """Handles the add timeline submission event acknowledgement."""
    modal = Modal(
        title="Add Timeline Event", close="Close", blocks=[Section(text="Adding timeline event...")]
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    AddTimelineEventActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_add_timeline_submission_event(
    ack: Ack,
    body: dict,
    user: DispatchUser,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
):
    """Handles the add timeline submission event."""
    ack_add_timeline_submission_event(ack=ack)

    event_date = form_data.get(DefaultBlockIds.date_picker_input)
    event_hour = form_data.get(DefaultBlockIds.hour_picker_input)["value"]
    event_minute = form_data.get(DefaultBlockIds.minute_picker_input)["value"]
    event_timezone_selection = form_data.get(DefaultBlockIds.timezone_picker_input)["value"]
    event_description = form_data.get(DefaultBlockIds.description_input)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=context["subject"].id, email=user.email
    )

    event_timezone = event_timezone_selection
    if event_timezone_selection == TimezoneOptions.local:
        participant_profile = get_user_profile_by_email(client, user.email)
        if participant_profile.get("tz"):
            event_timezone = participant_profile.get("tz")

    event_dt = datetime.fromisoformat(f"{event_date}T{event_hour}:{event_minute}")
    event_dt_utc = pytz.timezone(event_timezone).localize(event_dt).astimezone(pytz.utc)

    event_service.log_incident_event(
        db_session=db_session,
        source=f"Slack message from {participant.individual.name}",
        started_at=event_dt_utc,
        description=event_description,
        incident_id=context["subject"].id,
        individual_id=participant.individual.id,
        type=EventType.imported_message,
        owner=participant.individual.name,
    )

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Add Timeline Event",
        message="Timeline event added successfully.",
    )


def handle_update_participant_command(
    ack: Ack,
    body: dict,
    context: BoltContext,
    client: WebClient,
) -> None:
    """Handles the update participant command."""
    ack()

    if context["subject"].type == CaseSubjects.case:
        raise CommandError("Command is not currently available for cases.")

    incident = incident_service.get(
        db_session=context["db_session"], incident_id=context["subject"].id
    )

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="Use this form to update the reason why the participant was added to the incident."
                )
            ]
        ),
        participant_select(
            block_id=UpdateParticipantBlockIds.participant,
            participants=incident.participants,
        ),
        Input(
            element=PlainTextInput(placeholder="Reason for addition"),
            label="Reason added",
            block_id=UpdateParticipantBlockIds.reason,
        ),
    ]

    modal = Modal(
        title="Update Participant",
        blocks=blocks,
        submit="Update",
        close="Cancel",
        callback_id=UpdateParticipantActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_update_participant_submission_event(ack: Ack):
    """Handles the update participant submission event."""
    modal = Modal(
        title="Update Participant", close="Close", blocks=[Section(text="Updating participant...")]
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    UpdateParticipantActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_update_participant_submission_event(
    body: dict,
    ack: Ack,
    client: WebClient,
    db_session: Session,
    form_data: dict,
) -> None:
    """Handles the update participant submission event."""
    ack_update_participant_submission_event(ack=ack)

    added_reason = form_data.get(UpdateParticipantBlockIds.reason)
    participant_id = int(form_data.get(UpdateParticipantBlockIds.participant)["value"])
    selected_participant = participant_service.get(
        db_session=db_session, participant_id=participant_id
    )
    participant_service.update(
        db_session=db_session,
        participant=selected_participant,
        participant_in=ParticipantUpdate(added_reason=added_reason),
    )

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Update Participant",
        message="Participant added successfully.",
    )


def handle_update_notifications_group_command(
    ack: Ack, body: dict, context: BoltContext, client: WebClient, db_session: Session
) -> None:
    """Handles the update notification group command."""
    ack()

    # TODO handle cases
    if context["subject"].type == CaseSubjects.case:
        raise CommandError("Command is not currently available for cases.")

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    group_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )
    if not group_plugin:
        raise CommandError(
            "Group plugin is not enabled. Unable to update notifications group.",
        )

    if not incident.notifications_group:
        raise CommandError("No notification group available for this incident.")

    members = group_plugin.instance.list(incident.notifications_group.email)

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="Use this form to update the membership of the notifications group."
                )
            ]
        ),
        Input(
            label="Members",
            element=PlainTextInput(
                initial_value=", ".join(members),
                multiline=True,
                action_id=UpdateNotificationGroupActionIds.members,
            ),
            block_id=UpdateNotificationGroupBlockIds.members,
        ),
        Context(elements=[MarkdownText(text="Separate email addresses with commas")]),
    ]

    modal = Modal(
        title="Update Group Members",  # 24 Char Limit
        blocks=blocks,
        close="Cancel",
        submit="Update",
        callback_id=UpdateNotificationGroupActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_update_notifications_group_submission_event(ack: Ack):
    """Handles the update notifications group submission acknowledgement."""
    modal = Modal(
        title="Update Group Members",
        close="Close",
        blocks=[Section(text="Updating notifications group...")],
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    UpdateNotificationGroupActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_update_notifications_group_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
) -> None:
    """Handles the update notifications group submission event."""
    ack_update_notifications_group_submission_event(ack=ack)

    current_members = (
        body["view"]["blocks"][1]["element"]["initial_value"].replace(" ", "").split(",")
    )
    updated_members = (
        form_data.get(UpdateNotificationGroupBlockIds.members).replace(" ", "").split(",")
    )
    members_added = list(set(updated_members) - set(current_members))
    members_removed = list(set(current_members) - set(updated_members))

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    group_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )

    group_plugin.instance.add(incident.notifications_group.email, members_added)
    group_plugin.instance.remove(incident.notifications_group.email, members_removed)

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Update Group Members",
        message="Notification group members added successfully.",
    )


def handle_assign_role_command(
    ack: Ack, body: dict, context: BoltContext, client: WebClient
) -> None:
    """Handles the assign role command."""
    ack()

    roles = [
        {"text": r.value, "value": r.value}
        for r in ParticipantRoleType
        if r != ParticipantRoleType.participant
    ]

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="Assign a role to a participant. Note: The participant will be invited to the incident channel if they are not yet a member."
                )
            ]
        ),
        Input(
            block_id=AssignRoleBlockIds.user,
            label="Participant",
            element=UsersSelect(placeholder="Participant"),
        ),
        static_select_block(
            placeholder="Select Role", label="Role", options=roles, block_id=AssignRoleBlockIds.role
        ),
    ]

    modal = Modal(
        title="Assign Role",
        submit="Assign",
        close="Cancel",
        blocks=blocks,
        callback_id=AssignRoleActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_assign_role_submission_event(ack: Ack):
    """Handles the assign role submission acknowledgement."""
    modal = Modal(
        title="Assign Role", close="Close", blocks=[Section(text="Assigning role...")]
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    AssignRoleActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_assign_role_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    user: DispatchUser,
    form_data: dict,
) -> None:
    """Handles the assign role submission."""
    ack_assign_role_submission_event(ack=ack)
    assignee_user_id = form_data[AssignRoleBlockIds.user]["value"]
    assignee_role = form_data[AssignRoleBlockIds.role]["value"]
    assignee_email = get_user_email(client=client, user_id=assignee_user_id)

    # we assign the role
    incident_flows.incident_assign_role_flow(
        incident_id=context["subject"].id,
        assigner_email=user.email,
        assignee_email=assignee_email,
        assignee_role=assignee_role,
        db_session=db_session,
    )

    if (
        assignee_role == ParticipantRoleType.reporter
        or assignee_role == ParticipantRoleType.incident_commander  # noqa
    ):
        # we update the external ticket
        ticket_flows.update_incident_ticket(
            incident_id=context["subject"].id, db_session=db_session
        )

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Assign Role",
        message="Role assigned successfully.",
    )


def handle_engage_oncall_command(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    """Handles the engage oncall command."""
    ack()

    # TODO: handle cases
    if context["subject"].type == CaseSubjects.case:
        raise CommandError("Command is not currently available for cases.")

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    oncall_services = service_service.get_all_by_project_id_and_status(
        db_session=db_session, project_id=incident.project.id, is_active=True
    )

    if not oncall_services.count():
        raise CommandError(
            "No oncall services have been defined. You can define them in the Dispatch UI at /services."
        )

    services = [{"text": s.name, "value": s.external_id} for s in oncall_services]

    blocks = [
        static_select_block(
            label="Service",
            action_id=EngageOncallActionIds.service,
            block_id=EngageOncallBlockIds.service,
            placeholder="Select Service",
            options=services,
        ),
        Input(
            block_id=EngageOncallBlockIds.page,
            label="Page",
            element=Checkboxes(
                options=[PlainOption(text="Page", value="Yes")],
                action_id=EngageOncallActionIds.page,
            ),
            optional=True,
        ),
    ]

    modal = Modal(
        title="Engage Oncall",
        blocks=blocks,
        submit="Engage",
        close="Close",
        callback_id=EngageOncallActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_engage_oncall_submission_event(ack: Ack) -> None:
    """Handles engage oncall acknowledgment."""
    modal = Modal(
        title="Engage Oncall", close="Close", blocks=[Section(text="Engaging oncall...")]
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    EngageOncallActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_engage_oncall_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
) -> None:
    """Handles the engage oncall submission.

    Notes:
        If the page checkbox is checked, form_data will contain the `engage-oncall-page` key. For example:

        "engage-oncall-service": {
            "name": "Security Incident Response Team (SIRT) - TEST",
            "value": "1337WOW",
        },
        "engage-oncall-page": [{"name": "Page", "value": "Yes"}],

        Otherwise, the `engage-oncall-page` key is omitted. For example:

        "engage-oncall-service": {
            "name": "Security Incident Response Team (SIRT)",
            "value": "1337WOW",
        }
    """
    ack_engage_oncall_submission_event(ack=ack)
    oncall_service_external_id = form_data[EngageOncallBlockIds.service]["value"]
    page_block = form_data.get(EngageOncallBlockIds.page)
    page = page_block[0]["value"] if page_block else None  # page_block[0]["value"] == "Yes"

    oncall_individual, oncall_service = incident_flows.incident_engage_oncall_flow(
        user.email,
        context["subject"].id,
        oncall_service_external_id,
        page=page,
        db_session=db_session,
    )

    if not oncall_individual and not oncall_service:
        message = "Could not engage oncall. Oncall service plugin not enabled."

    if not oncall_individual and oncall_service:
        message = f"A member of {oncall_service.name} is already in the conversation."

    if oncall_individual and oncall_service:
        message = f"You have successfully engaged {oncall_individual.name} from the {oncall_service.name} oncall rotation."

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Engagement",
        message=message,
    )


def handle_report_tactical_command(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    """Handles the report tactical command."""
    ack()

    if context["subject"].type == CaseSubjects.case:
        raise CommandError("Command is not available outside of incident channels.")

    # we load the most recent tactical report
    tactical_report = report_service.get_most_recent_by_incident_id_and_type(
        db_session=db_session,
        incident_id=context["subject"].id,
        report_type=ReportTypes.tactical_report,
    )

    conditions = actions = needs = None
    if tactical_report:
        conditions = tactical_report.details.get("conditions")
        actions = tactical_report.details.get("actions")
        needs = tactical_report.details.get("needs")

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
    outstanding_actions = "" if actions is None else actions
    if incident.tasks:
        outstanding_actions += "\n\nOutstanding Incident Tasks:\n".join(
            [
                "-" + task.description
                for task in incident.tasks
                if task.status != TaskStatus.resolved
            ]
        )

    if len(outstanding_actions):
        actions = outstanding_actions

    blocks = [
        Input(
            label="Conditions",
            element=PlainTextInput(
                placeholder="Current incident conditions", initial_value=conditions, multiline=True
            ),
            block_id=ReportTacticalBlockIds.conditions,
        ),
        Input(
            label="Actions",
            element=PlainTextInput(
                placeholder="Current incident actions", initial_value=actions, multiline=True
            ),
            block_id=ReportTacticalBlockIds.actions,
        ),
        Input(
            label="Needs",
            element=PlainTextInput(
                placeholder="Current incident needs", initial_value=needs, multiline=True
            ),
            block_id=ReportTacticalBlockIds.needs,
        ),
    ]

    modal = Modal(
        title="Tactical Report",
        blocks=blocks,
        submit="Create",
        close="Close",
        callback_id=ReportTacticalActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_report_tactical_submission_event(ack: Ack) -> None:
    """Handles report tactical acknowledgment."""
    modal = Modal(
        title="Report Tactical", close="Close", blocks=[Section(text="Creating tactical report...")]
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    ReportTacticalActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_report_tactical_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    form_data: dict,
    user: DispatchUser,
) -> None:
    """Handles the report tactical submission"""
    ack_report_tactical_submission_event(ack=ack)
    tactical_report_in = TacticalReportCreate(
        conditions=form_data[ReportTacticalBlockIds.conditions],
        actions=form_data[ReportTacticalBlockIds.actions],
        needs=form_data[ReportTacticalBlockIds.needs],
    )

    report_flows.create_tactical_report(
        user_email=user.email,
        incident_id=context["subject"].id,
        tactical_report_in=tactical_report_in,
        organization_slug=context["subject"].organization_slug,
    )

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Tactical Report",
        message="Tactical report successfully created.",
    )


def handle_report_executive_command(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    """Handles executive report command."""
    ack()

    if context["subject"].type == CaseSubjects.case:
        raise CommandError("Command is not available outside of incident channels.")

    executive_report = report_service.get_most_recent_by_incident_id_and_type(
        db_session=db_session,
        incident_id=context["subject"].id,
        report_type=ReportTypes.executive_report,
    )

    current_status = overview = next_steps = None
    if executive_report:
        current_status = executive_report.details.get("current_status")
        overview = executive_report.details.get("overview")
        next_steps = executive_report.details.get("next_steps")

    blocks = [
        Input(
            label="Current Status",
            element=PlainTextInput(
                placeholder="Current status", initial_value=current_status, multiline=True
            ),
            block_id=ReportExecutiveBlockIds.current_status,
        ),
        Input(
            label="Overview",
            element=PlainTextInput(placeholder="Overview", initial_value=overview, multiline=True),
            block_id=ReportExecutiveBlockIds.overview,
        ),
        Input(
            label="Next Steps",
            element=PlainTextInput(
                placeholder="Next steps", initial_value=next_steps, multiline=True
            ),
            block_id=ReportExecutiveBlockIds.next_steps,
        ),
        Context(
            elements=[
                MarkdownText(
                    text=f"Use {context['config'].slack_command_update_notifications_group} to update the list of recipients of this report."
                )
            ]
        ),
    ]

    modal = Modal(
        title="Executive Report",
        blocks=blocks,
        submit="Create",
        close="Close",
        callback_id=ReportExecutiveActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_report_executive_submission_event(ack: Ack) -> None:
    """Handles executive submission acknowledgement."""
    modal = Modal(
        title="Executive Report",
        close="Close",
        blocks=[Section(text="Creating executive report...")],
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    ReportExecutiveActions.submit,
    middleware=[
        action_context_middleware,
        db_middleware,
        user_middleware,
        modal_submit_middleware,
        configuration_middleware,
    ],
)
def handle_report_executive_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
) -> None:
    """Handles the report executive submission."""
    ack_report_executive_submission_event(ack=ack)

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    executive_report_in = ExecutiveReportCreate(
        current_status=form_data[ReportExecutiveBlockIds.current_status],
        overview=form_data[ReportExecutiveBlockIds.overview],
        next_steps=form_data[ReportExecutiveBlockIds.next_steps],
    )

    executive_report = report_flows.create_executive_report(
        user_email=user.email,
        incident_id=incident.id,
        executive_report_in=executive_report_in,
        organization_slug=context["subject"].organization_slug,
    )

    blocks = []
    if executive_report and incident.notifications_group:
        blocks = [
            Section(text="Creating executive report... Success!"),
            Section(
                text=f"The executive report document has been created and can be found in the incident storage here: {executive_report.document.weblink}"
            ),
            Section(
                text=f"The executive report has been emailed to the incident notifications group: {incident.notifications_group.email}",
            ),
        ]
    else:
        blocks = [
            Section(text="Creating executive report... Failed!"),
            Section(
                text="The executive report document was not created successfully or the incident notifications group does not exist."
            ),
        ]

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Executive Report",
        blocks=blocks,
    )


def handle_update_incident_command(
    ack: Ack, body: dict, client: WebClient, context: BoltContext, db_session: Session
) -> None:
    """Creates the incident update modal."""
    ack()

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    blocks = [
        Context(elements=[MarkdownText(text="Use this form to update the incident's details.")]),
        title_input(initial_value=incident.title),
        description_input(initial_value=incident.description),
        resolution_input(initial_value=incident.resolution),
        incident_status_select(initial_option={"text": incident.status, "value": incident.status}),
        project_select(
            db_session=db_session,
            initial_option={"text": incident.project.name, "value": incident.project.id},
            action_id=IncidentUpdateActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(
            db_session=db_session,
            initial_option={
                "text": incident.incident_type.name,
                "value": incident.incident_type.id,
            },
            project_id=incident.project.id,
        ),
        incident_severity_select(
            db_session=db_session,
            initial_option={
                "text": incident.incident_severity.name,
                "value": incident.incident_severity.id,
            },
            project_id=incident.project.id,
        ),
        incident_priority_select(
            db_session=db_session,
            initial_option={
                "text": incident.incident_priority.name,
                "value": incident.incident_priority.id,
            },
            project_id=incident.project.id,
        ),
        tag_multi_select(
            optional=True,
            initial_options=[{"text": t.name, "value": t.id} for t in incident.tags],
        ),
    ]

    modal = Modal(
        title="Update Incident",
        blocks=blocks,
        submit="Update",
        close="Cancel",
        callback_id=IncidentUpdateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_incident_update_submission_event(ack: Ack) -> None:
    """Handles incident update submission event."""
    modal = Modal(
        title="Incident Update",
        close="Close",
        blocks=[Section(text="Updating incident...")],
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    IncidentUpdateActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_update_incident_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
) -> None:
    """Handles the update incident submission"""
    ack_incident_update_submission_event(ack=ack)
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    tags = []
    for t in form_data.get(DefaultBlockIds.tags_multi_select, []):
        # we have to fetch as only the IDs are embedded in slack
        tag = tag_service.get(db_session=db_session, tag_id=int(t["value"]))
        tags.append(tag)

    incident_in = IncidentUpdate(
        title=form_data[DefaultBlockIds.title_input],
        description=form_data[DefaultBlockIds.description_input],
        resolution=form_data[DefaultBlockIds.resolution_input],
        incident_type={"name": form_data[DefaultBlockIds.incident_type_select]["name"]},
        incident_severity={"name": form_data[DefaultBlockIds.incident_severity_select]["name"]},
        incident_priority={"name": form_data[DefaultBlockIds.incident_priority_select]["name"]},
        status=form_data[DefaultBlockIds.incident_status_select]["name"],
        tags=tags,
    )

    previous_incident = IncidentRead.from_orm(incident)

    # we currently don't allow users to update the incident's visibility,
    # costs, terms, or duplicates via Slack, so we copy them over
    incident_in.visibility = incident.visibility
    incident_in.incident_costs = incident.incident_costs
    incident_in.terms = incident.terms
    incident_in.duplicates = incident.duplicates

    updated_incident = incident_service.update(
        db_session=db_session, incident=incident, incident_in=incident_in
    )

    commander_email = updated_incident.commander.individual.email
    reporter_email = updated_incident.reporter.individual.email

    incident_flows.incident_update_flow(
        user.email,
        commander_email,
        reporter_email,
        context["subject"].id,
        previous_incident,
        db_session=db_session,
    )

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Update Incident",
        message="Incident updated successfully.",
    )


@app.shortcut(
    IncidentShortcutCallbacks.report, middleware=[db_middleware, shortcut_context_middleware]
)
def report_incident(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    shortcut: dict,
):
    ack()
    initial_description = None
    if body.get("message"):
        permalink = (
            client.chat_getPermalink(
                channel=context["subject"].channel_id, message_ts=body["message"]["ts"]
            )
        )["permalink"]
        initial_description = f"{body['message']['text']}\n\n{permalink}"

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="If you suspect an incident and need help, please fill out this form to the best of your abilities."
                )
            ]
        ),
        title_input(),
        description_input(initial_value=initial_description),
        project_select(
            db_session=db_session,
            action_id=IncidentReportActions.project_select,
            dispatch_action=True,
        ),
    ]

    modal = Modal(
        title="Report Incident",
        blocks=blocks,
        submit="Report",
        close="Cancel",
        callback_id=IncidentReportActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=shortcut["trigger_id"], view=modal)


def handle_report_incident_command(
    ack: Ack,
    body: dict,
    context: BoltContext,
    client: WebClient,
    db_session: Session,
) -> None:
    """Handles the report incident command."""
    ack()

    if body.get("channel_id"):
        context["subject"].channel_id = body["channel_id"]

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="If you suspect an incident and need help, please fill out this form to the best of your abilities."
                )
            ]
        ),
        title_input(),
        description_input(),
        project_select(
            db_session=db_session,
            action_id=IncidentReportActions.project_select,
            dispatch_action=True,
        ),
    ]

    modal = Modal(
        title="Report Incident",
        blocks=blocks,
        submit="Report",
        close="Cancel",
        callback_id=IncidentReportActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_report_incident_submission_event(ack: Ack) -> None:
    """Handles the report incident submission event acknowledgment."""
    modal = Modal(
        title="Report Incident",
        close="Close",
        blocks=[Section(text="Creating incident resources...")],
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    IncidentReportActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_report_incident_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
) -> None:
    """Handles the report incident submission"""
    ack_report_incident_submission_event(ack=ack)
    tags = []
    for t in form_data.get(DefaultBlockIds.tags_multi_select, []):
        # we have to fetch as only the IDs are embedded in Slack
        tag = tag_service.get(db_session=db_session, tag_id=int(t["value"]))
        tags.append(tag)

    project = {"name": form_data[DefaultBlockIds.project_select]["name"]}

    incident_type = None
    if form_data.get(DefaultBlockIds.incident_type_select):
        incident_type = {"name": form_data[DefaultBlockIds.incident_type_select]["name"]}

    incident_priority = None
    if form_data.get(DefaultBlockIds.incident_priority_select):
        incident_priority = {"name": form_data[DefaultBlockIds.incident_priority_select]["name"]}

    incident_severity = None
    if form_data.get(DefaultBlockIds.incident_severity_select):
        incident_severity = {"name": form_data[DefaultBlockIds.incident_severity_select]["name"]}

    incident_in = IncidentCreate(
        title=form_data[DefaultBlockIds.title_input],
        description=form_data[DefaultBlockIds.description_input],
        incident_type=incident_type,
        incident_priority=incident_priority,
        incident_severity=incident_severity,
        project=project,
        reporter=ParticipantUpdate(individual=IndividualContactRead(email=user.email)),
        tags=tags,
    )

    blocks = [
        Section(text="Creating your incident..."),
    ]

    modal = Modal(title="Incident Report", blocks=blocks, close="Close").build()

    result = client.views_update(
        view_id=body["view"]["id"],
        trigger_id=body["trigger_id"],
        view=modal,
    )

    # Create the incident
    incident = incident_service.create(db_session=db_session, incident_in=incident_in)

    blocks = [
        Section(
            text="This is a confirmation that you have reported an incident with the following information. You will be invited to an incident Slack conversation shortly."
        ),
        Section(text=f"*Title*\n {incident.title}"),
        Section(text=f"*Description*\n {incident.description}"),
        Section(
            fields=[
                MarkdownText(
                    text=f"*Commander*\n<{incident.commander.individual.weblink}|{incident.commander.individual.name}>"
                ),
                MarkdownText(text=f"*Type*\n {incident.incident_type.name}"),
                MarkdownText(text=f"*Severity*\n {incident.incident_severity.name}"),
                MarkdownText(text=f"*Priority*\n {incident.incident_priority.name}"),
            ]
        ),
    ]
    modal = Modal(title="Incident Report", blocks=blocks, close="Close").build()

    result = client.views_update(
        view_id=result["view"]["id"],
        trigger_id=result["trigger_id"],
        view=modal,
    )

    incident_flows.incident_create_flow(
        incident_id=incident.id,
        db_session=db_session,
        organization_slug=incident.project.organization.slug,
    )


@app.action(
    IncidentReportActions.project_select, middleware=[action_context_middleware, db_middleware]
)
def handle_report_incident_project_select_action(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    ack()
    values = body["view"]["state"]["values"]

    project_id = values[DefaultBlockIds.project_select][IncidentReportActions.project_select][
        "selected_option"
    ]["value"]

    context["subject"].project_id = project_id

    project = project_service.get(db_session=db_session, project_id=project_id)

    blocks = [
        Context(elements=[MarkdownText(text="Use this form to update the incident's details.")]),
        title_input(),
        description_input(),
        project_select(
            db_session=db_session,
            action_id=IncidentReportActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(db_session=db_session, project_id=project.id, optional=True),
        incident_severity_select(db_session=db_session, project_id=project.id, optional=True),
        incident_priority_select(db_session=db_session, project_id=project.id, optional=True),
        tag_multi_select(optional=True),
    ]

    modal = Modal(
        title="Report Incident",
        blocks=blocks,
        submit="Report",
        close="Cancel",
        callback_id=IncidentReportActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


# BUTTONS
@app.action(
    IncidentNotificationActions.invite_user, middleware=[button_context_middleware, db_middleware]
)
def handle_incident_notification_join_button_click(
    ack: Ack,
    client: WebClient,
    respond: Respond,
    db_session: Session,
    context: BoltContext,
):
    """Handles the incident join button click event."""
    ack()
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    if not incident:
        message = "Sorry, we can't invite you to this incident. The incident does not exist."
    elif incident.visibility == Visibility.restricted:
        message = "Sorry, we can't invite you to this incident. The incident's visibility is restricted. Please, reach out to the incident commander if you have any questions."
    elif incident.status == IncidentStatus.closed:
        message = "Sorry, you can't join this incident. The incident has already been marked as closed. Please, reach out to the incident commander if you have any questions."
    else:
        user_id = context["user_id"]
        try:
            client.conversations_invite(channel=incident.conversation.channel_id, users=[user_id])
            message = f"Success! We've added you to incident {incident.name}. Please, check your Slack sidebar for the new incident channel."
        except SlackApiError as e:
            if e.response.get("error") == SlackAPIErrorCode.ALREADY_IN_CHANNEL:
                message = f"Sorry, we can't invite you to this incident - you're already a member. Search for a channel called {incident.name.lower()} in your Slack sidebar."

    respond(text=message, response_type="ephemeral", replace_original=False, delete_original=False)


@app.action(
    IncidentNotificationActions.subscribe_user,
    middleware=[button_context_middleware, db_middleware],
)
def handle_incident_notification_subscribe_button_click(
    ack: Ack,
    client: WebClient,
    respond: Respond,
    db_session: Session,
    context: BoltContext,
):
    """Handles the incident subscribe button click event."""
    ack()
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    if not incident:
        message = "Sorry, we can't invite you to this incident. The incident does not exist."
    elif incident.visibility == Visibility.restricted:
        message = "Sorry, we can't invite you to this incident. The incident's visibility is restricted. Please, reach out to the incident commander if you have any questions."
    elif incident.status == IncidentStatus.closed:
        message = "Sorry, you can't subscribe to this incident. The incident has already been marked as closed. Please, reach out to the incident commander if you have any questions."
    else:
        user_id = context["user_id"]
        user_email = get_user_email(client=client, user_id=user_id)

        if incident.tactical_group:
            group_flows.update_group(
                subject=incident,
                group=incident.tactical_group,
                group_action=GroupAction.add_member,
                group_member=user_email,
                db_session=db_session,
            )
        message = f"Success! We've subscribed you to incident {incident.name}. You will start receiving all tactical reports about this incident via email."

    respond(text=message, response_type="ephemeral", replace_original=False, delete_original=False)


@app.action(
    LinkMonitorActionIds.monitor,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
def handle_monitor_link_monitor_button_click(
    ack: Ack,
    body: dict,
    context: BoltContext,
    db_session: Session,
    respond: Respond,
    user: DispatchUser,
) -> None:
    """Handles the monitor button in the handle_message_monitor() event."""
    ack()

    message = monitor_link_button_click(
        body=body,
        context=context,
        db_session=db_session,
        enabled=True,
        email=user.email,
    )

    respond(
        text=message,
        response_type="ephemeral",
        delete_original=False,
        replace_original=False,
    )


@app.action(
    LinkMonitorActionIds.ignore,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
def handle_monitor_link_ignore_button_click(
    ack: Ack,
    body: dict,
    context: BoltContext,
    db_session: Session,
    respond: Respond,
    user: DispatchUser,
) -> None:
    """Handles the ignore button in the handle_message_monitor() event."""
    ack()

    message = monitor_link_button_click(
        body=body,
        context=context,
        db_session=db_session,
        enabled=False,
        email=user.email,
    )

    respond(
        text=message,
        response_type="ephemeral",
        delete_original=False,
        replace_original=False,
    )


def monitor_link_button_click(
    body: dict,
    context: BoltContext,
    db_session: Session,
    enabled: bool,
    email: str,
) -> str:
    """Core logic for handle_message_monitor() button click that builds MonitorCreate object and message."""

    button = MonitorMetadata.parse_raw((body["actions"][0]["value"]))
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
    plugin_instance = plugin_service.get_instance(
        db_session=db_session, plugin_instance_id=button.plugin_instance_id
    )

    creator = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=email
    )

    monitor_in = MonitorCreate(
        incident=incident,
        enabled=enabled,
        plugin_instance=plugin_instance,
        creator=creator,
        weblink=button.weblink,
    )

    monitor_service.create_or_update(db_session=db_session, monitor_in=monitor_in)

    return (
        f"A new monitor instance has been created.\n\n *Weblink:* {button.weblink}"
        if enabled is True
        else f"This monitor is now ignored. Dispatch won't remind this incident channel about it again.\n\n *Weblink:* {button.weblink}"
    )


@app.action(
    TaskNotificationActionIds.update_status,
    middleware=[button_context_middleware, db_middleware],
)
def handle_update_task_status_button_click(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
):
    """Handles the update task button in the list-my-tasks message."""
    ack()

    button = TaskMetadata.parse_raw(body["actions"][0]["value"])

    resolve = True
    if button.action_type == "reopen":
        resolve = False

    # When the task originated from the Dispatch front-end.
    # Tasks created in the front-end do not have an associated "resource".
    # Thus, no "resource_id" entry is necessary.
    from_drive = True if button.resource_id is not None else False

    if from_drive:
        # When the task originated from the drive plugin
        task = task_service.get_by_resource_id(
            db_session=db_session, resource_id=button.resource_id
        )
    else:
        task = task_service.get(db_session=db_session, task_id=button.task_id)

    # avoid external calls if we are already in the desired state
    if resolve and task.status == TaskStatus.resolved:
        return

    if not resolve and task.status == TaskStatus.open:
        return

    if from_drive:
        # we don't currently have a good way to get the correct file_id (we don't store a task <-> relationship)
        # lets try in both the incident doc and PIR doc
        drive_task_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=task.incident.project.id, plugin_type="task"
        )
        try:
            file_id = task.incident.incident_document.resource_id
            drive_task_plugin.instance.update(file_id, button.resource_id, resolved=resolve)
        except DispatchException:
            file_id = task.incident.incident_review_document.resource_id
            drive_task_plugin.instance.update(file_id, button.resource_id, resolved=resolve)
    else:
        status = TaskStatus.resolved if resolve is True else TaskStatus.open
        task_service.resolve_or_reopen(db_session=db_session, task_id=task.id, status=status)

    tasks = task_service.get_all_by_incident_id(
        db_session=db_session,
        incident_id=context["subject"].id,
    )

    tasks = task_service.get_all_by_incident_id(
        db_session=db_session,
        incident_id=context["subject"].id,
    )

    draw_task_modal(
        channel_id=button.channel_id,
        client=client,
        first_open=False,
        view_id=body["view"]["id"],
        tasks=tasks,
    )


@app.action(RemindAgainActions.submit, middleware=[select_context_middleware, db_middleware])
def handle_remind_again_select_action(
    ack: Ack,
    body: dict,
    context: BoltContext,
    db_session: Session,
    respond: Respond,
    user: DispatchUser,
) -> None:
    """Handles remind again select event."""
    ack()
    try:
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

        # User-selected option as org-id-report_type-delay
        value = body["actions"][0]["selected_option"]["value"]

        # Parse out report type and selected delay
        *_, report_type, selection = value.split("-")
        selection_as_message = reminder_select_values[selection]["message"]
        hours = reminder_select_values[selection]["value"]

        # Get new remind time
        delay_to_time = datetime.utcnow() + timedelta(hours=hours)

        # Store in incident
        if report_type == ReportTypes.tactical_report:
            incident.delay_tactical_report_reminder = delay_to_time
        elif report_type == ReportTypes.executive_report:
            incident.delay_executive_report_reminder = delay_to_time

        db_session.add(incident)
        db_session.commit()

        message = f"Success! We'll remind you again in {selection_as_message}."
        respond(
            text=message, response_type="ephemeral", replace_original=False, delete_original=False
        )
    except Exception as e:
        guid = str(uuid.uuid4())
        log.error(f"ERROR trying to save reminder delay with guid {guid}.")
        log.exception(e)
        message = build_unexpected_error_message(guid)
        respond(
            text=message, response_type="ephemeral", replace_original=False, delete_original=False
        )
