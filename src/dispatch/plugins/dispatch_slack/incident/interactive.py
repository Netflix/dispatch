import logging
from datetime import datetime
from typing import Any, List

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
from slack_bolt.async_app import AsyncAck, AsyncBoltContext, AsyncRespond
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy import func
from sqlalchemy.orm import Session

from dispatch.auth import service as user_service
from dispatch.auth.models import DispatchUser, UserRegister
from dispatch.config import DISPATCH_UI_URL
from dispatch.database.core import engine, resolve_attr, sessionmaker
from dispatch.database.service import search_filter_sort_paginate
from dispatch.document import service as document_service
from dispatch.enums import Visibility
from dispatch.event import service as event_service
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import IncidentCreate, IncidentRead, IncidentUpdate
from dispatch.individual import service as individual_service
from dispatch.individual.models import IndividualContactRead
from dispatch.messaging.strings import INCIDENT_RESOURCES_MESSAGE, MessageType
from dispatch.monitor import service as monitor_service
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantUpdate
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.enums import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.decorators import message_dispatcher, handle_lazy_error
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
    IncidentReportActions,
    IncidentUpdateActions,
    IncidentUpdateBlockIds,
    LinkMonitorActionIds,
    LinkMonitorBlockIds,
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
from dispatch.plugins.dispatch_slack.messaging import (
    create_message_blocks,
    get_incident_conversation_command_message,
)
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    command_context_middleware,
    configuration_middleware,
    db_middleware,
    message_context_middleware,
    modal_submit_middleware,
    restricted_command_middleware,
    user_middleware,
)
from dispatch.plugins.dispatch_slack.models import SubjectMetadata
from dispatch.plugins.dispatch_slack.service import (
    chunks,
    get_user_email_async,
    get_user_profile_by_email_async,
)
from dispatch.project import service as project_service
from dispatch.report import flows as report_flows
from dispatch.report import service as report_service
from dispatch.report.enums import ReportTypes
from dispatch.report.models import ExecutiveReportCreate, TacticalReportCreate
from dispatch.service import service as service_service
from dispatch.tag import service as tag_service
from dispatch.tag.models import Tag
from dispatch.task import service as task_service
from dispatch.task.enums import TaskStatus
from dispatch.task.models import Task

log = logging.getLogger(__file__)


class TaskMetadata(SubjectMetadata):
    resource_id: str


class MonitorMetadata(SubjectMetadata):
    weblink: str


def configure(config):
    """Maps commands/events to their functions."""
    middleware = [
        command_context_middleware,
        db_middleware,
        configuration_middleware,
    ]

    # don't need an incident context
    app.command(
        config.slack_command_list_incidents,
        middleware=middleware,
    )(ack=ack_command, lazy=[handle_list_incidents_command])

    app.command(config.slack_command_report_incident, middleware=middleware)(
        handle_report_incident_command
    )

    # non-sensitive-commands
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
    app.command(config.slack_command_list_resources, middleware=middleware)(
        handle_list_resources_command
    )
    app.command(config.slack_command_engage_oncall, middleware=middleware)(
        handle_engage_oncall_command
    )

    # sensitive commands
    middleware.extend([user_middleware, restricted_command_middleware])
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

    # required to allow the user to change the reaction string
    app.event(
        {"type": "reaction_added", "reaction": config.timeline_event_reaction},
        middleware=[db_middleware],
    )(handle_timeline_added_event)


def refetch_db_session(organization_slug: str) -> Session:
    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"dispatch_organization_{organization_slug}",
        }
    )
    db_session = sessionmaker(bind=schema_engine)()
    return db_session


@app.options(
    DefaultActionIds.tags_multi_select, middleware=[action_context_middleware, db_middleware]
)
async def handle_tag_search_action(
    ack: AsyncAck, payload: dict, context: AsyncBoltContext, db_session: Session
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

    await ack(options=options)


@app.action(
    IncidentUpdateActions.project_select, middleware=[action_context_middleware, db_middleware]
)
async def handle_update_incident_project_select_action(
    ack: AsyncAck,
    body: dict,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    db_session: Session,
) -> None:
    await ack()
    values = body["view"]["state"]["values"]

    project_id = values[DefaultBlockIds.project_select][IncidentUpdateActions.project_select][
        "selected_option"
    ]["value"]

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

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


# COMMANDS
@handle_lazy_error
async def handle_list_incidents_command(
    payload: dict,
    respond: AsyncRespond,
    context: AsyncBoltContext,
) -> None:
    """Handles the list incidents command."""
    projects = []

    db_session = refetch_db_session(context["subject"].organization_slug)

    if context["subject"].type == "incident":
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
                await respond(
                    text=f"Project name '{args[1]}' in organization '{args[0]}' not found. Check your spelling.",
                    response_type="ephemeral",
                )
                return
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

    blocks = [Section(text="*Incident List*")]

    if incidents:
        for incident in incidents:
            if incident.visibility == Visibility.open:
                incident_weblink = f"{DISPATCH_UI_URL}/{incident.project.organization.name}/incidents/{incident.name}?project={incident.project.name}"

                blocks.append(Section(text=f"*<{incident_weblink}|{incident.name}>*"))
                blocks.append(
                    Section(
                        fields=[
                            f"*Title*\n {incident.title}",
                            f"*Commander*\n<{incident.commander.individual.weblink}|{incident.commander.individual.name}>",
                            f"*Project*\n{incident.project.name}",
                            f"*Status*\n{incident.status}",
                            f"*Type*\n {incident.incident_type.name}",
                            f"*Severity*\n {incident.incident_severity.name}",
                            f"*Priority*\n {incident.incident_priority.name}",
                        ]
                    )
                )
                blocks.append(Divider())

    for c in chunks(blocks, 50):
        blocks = Message(blocks=c).build()["blocks"]
        await respond(text="Incident List", blocks=blocks, response_type="ephemeral")


async def handle_list_participants_command(
    ack: AsyncAck,
    respond: AsyncRespond,
    client: AsyncWebClient,
    db_session: Session,
    context: AsyncBoltContext,
) -> None:
    """Handles list participants command."""
    await ack()
    blocks = [Section(text="*Incident Participants*")]
    participants = participant_service.get_all_by_incident_id(
        db_session=db_session, incident_id=context["subject"].id
    ).all()

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    contact_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="contact"
    )
    if not contact_plugin:
        await respond(
            text="Contact plugin is not enabled. Unable to list participants.",
            response_type="ephemeral",
        )
        return

    for participant in participants:
        if participant.active_roles:
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
                participant_avatar_url = await dispatch_slack_service.get_user_avatar_url_async(
                    client, participant_email
                )
                accessory = Image(image_url=participant_avatar_url, alt_text=participant_name)

            blocks.extend(
                [
                    Section(
                        fields=[
                            f"*Name* \n<{participant_weblink}|{participant_name} ({participant_email})>",
                            f"*Team*\n {participant_team}, {participant_department}",
                            f"*Location* \n{participant_location}",
                            f"*Incident Role(s)* \n{(', ').join(participant_roles)}",
                        ],
                        accessory=accessory,
                    ),
                    Divider(),
                ]
            )

    blocks = Message(blocks=blocks).build()["blocks"]
    await respond(text="Incident Participant List", blocks=blocks, response_type="ephemeral")


def filter_tasks_by_assignee_and_creator(
    tasks: List[Task], by_assignee: str, by_creator: str
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


async def handle_list_tasks_command(
    ack: AsyncAck,
    body: dict,
    payload: dict,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    db_session: Session,
    respond: AsyncRespond,
) -> None:
    """Handles the list tasks command."""
    await ack()
    blocks = []

    caller_only = False
    if body["command"] == context["config"].slack_command_list_my_tasks:
        caller_only = True

    for status in TaskStatus:
        blocks.append(Section(text=f"*{status} Incident Tasks*"))
        button_text = "Resolve" if status == TaskStatus.open else "Re-open"

        tasks = task_service.get_all_by_incident_id_and_status(
            db_session=db_session, incident_id=context["subject"].id, status=status
        )

        if caller_only:
            user_id = payload["user_id"]
            email = (await client.users_info(user=user_id))["user"]["profile"]["email"]
            user = user_service.get_or_create(
                db_session=db_session,
                organization=context["subject"].organization_slug,
                user_in=UserRegister(email=email),
            )
            tasks = filter_tasks_by_assignee_and_creator(tasks, user.email, user.email)

        if not tasks:
            blocks.append(Section(text="No tasks."))

        for idx, task in enumerate(tasks):
            assignees = [f"<{a.individual.weblink}|{a.individual.name}>" for a in task.assignees]

            button_metadata = TaskMetadata(
                type="incident",
                organization_slug=task.project.organization.slug,
                id=task.incident.id,
                project_id=task.project.id,
                resource_id=task.resource_id,
                channel_id=context["channel_id"],
            ).json()

            blocks.append(
                Section(
                    fields=[
                        f"*Description:* \n <{task.weblink}|{task.description}>",
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
            blocks.append(Divider())

    message = Message(blocks=blocks).build()["blocks"]
    await respond(text="Incident Task List", blocks=message, response_type="ephermeral")


async def handle_list_resources_command(
    ack: AsyncAck, respond: AsyncRespond, db_session: Session, context: AsyncBoltContext
) -> None:
    """Handles the list resources command."""
    await ack()

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    incident_description = (
        incident.description
        if len(incident.description) <= 500
        else f"{incident.description[:500]}..."
    )

    # we send the ephemeral message
    message_kwargs = {
        "title": incident.title,
        "description": incident_description,
        "commander_fullname": incident.commander.individual.name,
        "commander_team": incident.commander.team,
        "commander_weblink": incident.commander.individual.weblink,
        "reporter_fullname": incident.reporter.individual.name,
        "reporter_team": incident.reporter.team,
        "reporter_weblink": incident.reporter.individual.weblink,
        "document_weblink": resolve_attr(incident, "incident_document.weblink"),
        "storage_weblink": resolve_attr(incident, "storage.weblink"),
        "conference_weblink": resolve_attr(incident, "conference.weblink"),
        "conference_challenge": resolve_attr(incident, "conference.conference_challenge"),
    }

    faq_doc = document_service.get_incident_faq_document(
        db_session=db_session, project_id=incident.project_id
    )
    if faq_doc:
        message_kwargs.update({"faq_weblink": faq_doc.weblink})

    conversation_reference = document_service.get_conversation_reference_document(
        db_session=db_session, project_id=incident.project_id
    )
    if conversation_reference:
        message_kwargs.update(
            {"conversation_commands_reference_document_weblink": conversation_reference.weblink}
        )

    blocks = create_message_blocks(
        INCIDENT_RESOURCES_MESSAGE, MessageType.incident_resources_message, **message_kwargs
    )
    blocks = Message(blocks=blocks).build()["blocks"]
    await respond(text="Incident Resources", blocks=blocks, response_type="ephemeral")


async def ack_command(ack: AsyncAck, context: AsyncBoltContext, payload: dict) -> None:
    """Handles request acknowledgement for slash commands."""
    message = get_incident_conversation_command_message(
        config=context.get("config"), command_string=payload.get("command")
    )

    if isinstance(message, str):
        # if message is a string, no custom message was found.
        # avoid calling .get() on a string and default to an ephemeral message.
        text = message
        response_type = "ephemeral"
    elif isinstance(message, dict):
        # if message is a dict, we found a corresponding user response.
        text = message.get("text")
        response_type = message.get("response_type")
    else:
        # something went very wrong, we ack() without a response, and move on.
        await ack()

    await ack(text=text, response_type=response_type)


# EVENTS


async def handle_timeline_added_event(
    client: Any, context: AsyncBoltContext, payload: Any, db_session: Session
) -> None:
    """Handles an event where a reaction is added to a message."""
    conversation_id = context["channel_id"]
    message_ts = payload["item"]["ts"]
    message_ts_utc = datetime.utcfromtimestamp(float(message_ts))

    # we fetch the message information
    response = await dispatch_slack_service.list_conversation_messages(
        client, conversation_id, latest=message_ts, limit=1, inclusive=1
    )
    message_text = response["messages"][0]["text"]
    message_sender_id = response["messages"][0]["user"]

    # TODO: (wshel) handle case reactions
    if context["subject"].type == "incident":
        # we fetch the incident
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

        # we fetch the individual who sent the message
        message_sender_email = await get_user_email_async(client=client, user_id=message_sender_id)
        individual = individual_service.get_by_email_and_project(
            db_session=db_session, email=message_sender_email, project_id=incident.project.id
        )

        # we log the event
        event_service.log_incident_event(
            db_session=db_session,
            source="Slack Plugin - Conversation Management",
            description=f'"{message_text}," said {individual.name}',
            incident_id=context["subject"].id,
            individual_id=individual.id,
            started_at=message_ts_utc,
        )


@message_dispatcher.add(
    exclude={"subtype": ["channel_join", "channel_leave"]}
)  # we ignore channel join and leave messages
async def handle_participant_role_activity(
    ack: AsyncAck, db_session: Session, context: AsyncBoltContext, user: DispatchUser
) -> None:
    """
    Increments the participant role's activity counter and assesses the need of changing
    a participant's role based on its activity and changes it if needed.
    """
    await ack()

    # TODO: add when case support when participants are added.
    if context["subject"].type == "incident":
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
                        )

            db_session.commit()


@message_dispatcher.add(
    exclude={"subtype": ["channel_join", "group_join"]}
)  # we ignore user channel and group join messages
async def handle_after_hours_message(
    ack: AsyncAck,
    context: AsyncBoltContext,
    client: AsyncWebClient,
    payload: dict,
    user: DispatchUser,
    db_session: Session,
) -> None:
    """Notifies the user that this incident is currently in after hours mode."""
    await ack()

    if context["subject"].type == "incident":
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        owner_email = incident.commander.individual.email
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=user.email
        )
        # get their timezone from slack
        owner_tz = (
            await dispatch_slack_service.get_user_info_by_email_async(client, email=owner_email)
        )["tz"]
        message = f"Responses may be delayed. The current incident priority is *{incident.incident_priority.name}* and your message was sent outside of the Incident Commander's working hours (Weekdays, 9am-5pm, {owner_tz} timezone)."
    else:
        # TODO: add case support
        return

    now = datetime.now(pytz.timezone(owner_tz))
    is_business_hours = now.weekday() not in [5, 6] and 9 <= now.hour < 17

    if not is_business_hours:
        if not participant.after_hours_notification:
            participant.after_hours_notification = True
            db_session.add(participant)
            db_session.commit()
            await client.chat_postEphemeral(
                text=message,
                channel=payload["channel"],
                user=payload["user"],
            )


@message_dispatcher.add()
async def handle_thread_creation(
    client: AsyncWebClient, payload: dict, context: AsyncBoltContext
) -> None:
    """Sends the user an ephemeral message if they use threads."""
    if not context["config"].ban_threads:
        return

    if context["subject"].type == "incident":
        if payload.get("thread_ts"):
            message = "Please refrain from using threads in incident channels. Threads make it harder for incident participants to maintain context."
            await client.chat_postEphemeral(
                text=message,
                channel=payload["channel"],
                thread_ts=payload["thread_ts"],
                user=payload["user"],
            )


@message_dispatcher.add()
async def handle_message_tagging(
    db_session: Session, payload: dict, context: AsyncBoltContext
) -> None:
    """Looks for incident tags in incident messages."""

    # TODO: (wshel) handle case tagging
    if context["subject"].type == "incident":
        text = payload["text"]
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        tags = tag_service.get_all(db_session=db_session, project_id=incident.project.id).all()
        tag_strings = [t.name.lower() for t in tags if t.discoverable]
        phrases = build_term_vocab(tag_strings)
        matcher = build_phrase_matcher("dispatch-tag", phrases)
        extracted_tags = list(set(extract_terms_from_text(text, matcher)))

        matched_tags = (
            db_session.query(Tag)
            .filter(func.upper(Tag.name).in_([func.upper(t) for t in extracted_tags]))
            .all()
        )

        incident.tags.extend(matched_tags)
        db_session.commit()


@message_dispatcher.add()
async def handle_message_monitor(
    ack: AsyncAck,
    payload: dict,
    context: AsyncBoltContext,
    client: AsyncWebClient,
    db_session: Session,
    respond: AsyncRespond,
) -> None:
    """Looks for strings that are available for monitoring (e.g. links)."""
    await ack()

    if context["subject"].type == "incident":
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        project_id = incident.project.id
    else:
        # TODO: handle cases
        await respond(
            text="Command is not currently available for cases.", response_type="ephemeral"
        )
        return

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
                        type="incident",
                        organization_slug=incident.project.organization.slug,
                        id=incident.id,
                        project_id=incident.project.id,
                        channel_id=context["channel_id"],
                        weblink=match_data["weblink"],
                    )

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
                    await client.chat_postEphemeral(
                        text="Link Monitor",
                        channel=payload["channel"],
                        thread_ts=payload["thread_ts"],
                        blocks=blocks,
                        user=payload["user"],
                    )


@app.event(
    "member_joined_channel",
    middleware=[
        message_context_middleware,
        user_middleware,
        db_middleware,
        configuration_middleware,
    ],
)
async def handle_member_joined_channel(
    ack: AsyncAck,
    user: DispatchUser,
    body: dict,
    client: AsyncWebClient,
    db_session: Session,
    context: AsyncBoltContext,
) -> None:
    """Handles the member_joined_channel Slack event."""
    await ack()

    participant = incident_flows.incident_add_or_reactivate_participant_flow(
        user_email=user.email, incident_id=context["subject"].id, db_session=db_session
    )

    # If the user was invited, the message will include an inviter property containing the user ID of the inviting user.
    # The property will be absent when a user manually joins a channel, or a user is added by default (e.g. #general channel).
    inviter = body.get("event", {}).get("inviter", None)
    inviter_is_user = (
        dispatch_slack_service.is_user(context["config"], inviter) if inviter else None
    )

    if inviter and inviter_is_user:
        # Participant is added into the incident channel using an @ message or /invite command.
        inviter_email = await get_user_email_async(client=client, user_id=inviter)
        added_by_participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=inviter_email
        )
        participant.added_by = added_by_participant
    else:
        # User joins via the `join` button on Web Application or Slack.
        # We default to the incident commander when we don't know who added the user or the user is the Dispatch bot.
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        participant.added_by = incident.commander

    # Message text when someone @'s a user is not available in body, use generic added by reason
    participant.added_reason = f"Participant added by {participant.added_by}"

    db_session.add(participant)
    db_session.commit()


@app.event(
    "member_left_channel", middleware=[message_context_middleware, user_middleware, db_middleware]
)
async def handle_member_left_channel(
    ack: AsyncAck, context: AsyncBoltContext, db_session: Session, user: DispatchUser
) -> None:
    await ack()

    incident_flows.incident_remove_participant_flow(
        user.email, context["subject"].id, db_session=db_session
    )


# MODALS
async def handle_add_timeline_event_command(
    ack: AsyncAck, body: dict, client: AsyncWebClient, context: AsyncBoltContext
) -> None:
    """Handles the add timeline event command."""
    await ack()
    blocks = [
        Context(
            elements=[
                MarkdownText(text="Use this form to add an event to the incident's timeline.")
            ]
        ),
        description_input(),
    ]

    blocks.extend(datetime_picker_block())

    modal = Modal(
        title="Add Timeline Event",
        blocks=blocks,
        submit="Add",
        close="Close",
        callback_id=AddTimelineEventActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(
        trigger_id=body["trigger_id"],
        view=modal,
    )


async def ack_add_timeline_submission_event(ack: AsyncAck) -> None:
    """Handles the add timeline submission event acknowledgement."""
    modal = Modal(
        title="Add Timeline Event", close="Close", blocks=[Section(text="Adding timeline event...")]
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_add_timeline_submission_event(
    body: dict,
    user: DispatchUser,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    form_data: dict,
):
    """Handles the add timeline submission event."""
    # refetch session as we can't pass a db_session lazily, these could be moved to @background_task functions
    # in the future
    db_session = refetch_db_session(context["subject"].organization_slug)
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
        participant_profile = await get_user_profile_by_email_async(client, user.email)
        if participant_profile.get("tz"):
            event_timezone = participant_profile.get("tz")

    event_dt = datetime.fromisoformat(f"{event_date}T{event_hour}:{event_minute}")
    event_dt_utc = pytz.timezone(event_timezone).localize(event_dt).astimezone(pytz.utc)

    event_service.log_incident_event(
        db_session=db_session,
        source="Slack Plugin - Conversation Management",
        started_at=event_dt_utc,
        description=f'"{event_description}," said {participant.individual.name}',
        incident_id=context["subject"].id,
        individual_id=participant.individual.id,
    )

    modal = Modal(
        title="Add Timeline Event",
        close="Close",
        blocks=[Section(text="Adding timeline event... Success!")],
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


app.view(
    AddTimelineEventActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)(ack=ack_add_timeline_submission_event, lazy=[handle_add_timeline_submission_event])


async def handle_update_participant_command(
    ack: AsyncAck,
    respond: AsyncRespond,
    body: dict,
    context: AsyncBoltContext,
    db_session: Session,
    client: AsyncWebClient,
) -> None:
    """Handles the update participant command."""
    await ack()

    if context["subject"].type == "case":
        await respond(
            text="Command is not currently available for cases.", response_type="ephemeral"
        )
        return

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

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

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def ack_update_participant_submission_event(ack):
    """Handles the update participant submission event."""
    modal = Modal(
        title="Update Participant", close="Close", blocks=[Section(text="Updating participant...")]
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_update_participant_submission_event(
    body: dict,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    db_session: Session,
    form_data: dict,
) -> None:
    """Handles the update participant submission event."""
    # refetch session as we can't pass a db_session lazily, these could be moved to @background_task functions
    # in the future
    db_session = refetch_db_session(context["subject"].organization_slug)
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
    modal = Modal(
        title="Update Participant",
        close="Close",
        blocks=[Section(text="Updating participant...Success!")],
    ).build()
    await client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


app.view(
    UpdateParticipantActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)(ack=ack_update_participant_submission_event, lazy=[handle_update_participant_submission_event])


async def handle_update_notifications_group_command(
    ack: AsyncAck,
    respond: AsyncRespond,
    body: dict,
    context: AsyncBoltContext,
    client: AsyncWebClient,
    db_session: Session,
) -> None:
    """Handles the update notification group command."""
    await ack()

    # TODO handle cases
    if context["subject"].type == "case":
        await respond(
            text="Command is not currently available for cases.", response_type="ephemeral"
        )
        return

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    group_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )
    if not group_plugin:
        await respond(
            text="Group plugin is not enabled. Unable to update notifications group.",
            response_type="ephemeral",
        )
        return

    if not incident.notifications_group:
        await respond(
            text="No notification group available for this incident.", response_type="ephemeral"
        )
        return

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

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def ack_update_notifications_group_submission_event(ack):
    """Handles the update notifications group submission acknowledgement."""
    modal = Modal(
        title="Update Group Members",
        close="Close",
        blocks=[Section(text="Updating notifications group...")],
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_update_notifications_group_submission_event(
    body: dict,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    form_data: dict,
) -> None:
    """Handles the update notifications group submission event."""
    # refetch session as we can't pass a db_session lazily, these could be moved to @background_task functions
    # in the future
    db_session = refetch_db_session(context["subject"].organization_slug)

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

    modal = Modal(
        title="Update Group Members",
        blocks=[Section(text="Updating notification group members... Success!")],
        close="Close",
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


app.view(
    UpdateNotificationGroupActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)(
    ack=ack_update_notifications_group_submission_event,
    lazy=[handle_update_notifications_group_submission_event],
)


async def handle_assign_role_command(
    ack: AsyncAck, context: AsyncBoltContext, body: dict, client: AsyncWebClient
) -> None:
    """Handles the assign role command."""
    await ack()

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
    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def ack_assign_role_submission_event(ack: AsyncAck):
    """Handles the assign role submission acknowledgement."""
    modal = Modal(
        title="Assign Role", close="Close", blocks=[Section(text="Assigning role...")]
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_assign_role_submission_event(
    body: dict,
    user: DispatchUser,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    form_data: dict,
) -> None:
    """Handles the assign role submission."""
    # refetch session as we can't pass a db_session lazily, these could be moved to @background_task functions
    # in the future
    db_session = refetch_db_session(context["subject"].organization_slug)

    assignee_user_id = form_data[AssignRoleBlockIds.user]["value"]
    assignee_role = form_data[AssignRoleBlockIds.role]["value"]
    assignee_email = await get_user_email_async(client=client, user_id=assignee_user_id)

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
        incident_flows.update_external_incident_ticket(
            incident_id=context["subject"].id, db_session=db_session
        )

    modal = Modal(
        title="Assign Role", blocks=[Section(text="Assigning role... Success!")], close="Close"
    ).build()
    await client.views_update(view_id=body["view"]["id"], view=modal)


app.view(
    AssignRoleActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)(ack=ack_assign_role_submission_event, lazy=[handle_assign_role_submission_event])


async def handle_engage_oncall_command(
    ack: AsyncAck,
    respond: AsyncRespond,
    context: AsyncBoltContext,
    body: dict,
    client: AsyncWebClient,
    db_session: Session,
) -> None:
    """Handles the engage oncall command."""
    await ack()

    # TODO: handle cases
    if context["subject"].type == "case":
        await respond(
            text="Command is not currently available for cases.", response_type="ephemeral"
        )
        return

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    oncall_services = service_service.get_all_by_project_id_and_status(
        db_session=db_session, project_id=incident.project.id, is_active=True
    )

    if not oncall_services.count():
        await respond(
            blocks=Message(
                blocks=[
                    Section(
                        text="No oncall services have been defined. You can define them in the Dispatch UI at /services."
                    )
                ]
            ).build()["blocks"],
            response_type="ephemeral",
        )
        return

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
    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def ack_engage_oncall_submission_event(ack: AsyncAck) -> None:
    """Handles engage oncall acknowledgment."""
    modal = Modal(
        title="Engage Oncall", close="Close", blocks=[Section(text="Engaging oncall...")]
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_engage_oncall_submission_event(
    client: AsyncWebClient,
    body: dict,
    user: DispatchUser,
    context: AsyncBoltContext,
    form_data: dict,
) -> None:
    """Handles the engage oncall submission"""
    # refetch session as we can't pass a db_session lazily, these could be moved to @background_task functions
    # in the future
    db_session = refetch_db_session(context["subject"].organization_slug)

    oncall_service_external_id = form_data[EngageOncallBlockIds.service]["value"]
    page = form_data.get(EngageOncallBlockIds.page, {"value": None})["value"]

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

    modal = Modal(title="Engagement", blocks=[Section(text=message)], close="Close").build()
    await client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


app.view(
    EngageOncallActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)(ack=ack_engage_oncall_submission_event, lazy=[handle_engage_oncall_submission_event])


async def handle_report_tactical_command(
    ack: AsyncAck,
    client: AsyncWebClient,
    respond: AsyncRespond,
    context: AsyncBoltContext,
    db_session: Session,
    body: dict,
) -> None:
    """Handles the report tactical command."""
    await ack()

    if context["subject"].type == "case":
        await respond(
            text="Command is not available outside of incident channels.", response_type="ephemeral"
        )
        return

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

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def ack_report_tactical_submission_event(ack: AsyncAck) -> None:
    """Handles report tactical acknowledgment."""
    modal = Modal(
        title="Report Tactical", close="Close", blocks=[Section(text="Creating tactical report...")]
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_report_tactical_submission_event(
    client: AsyncWebClient,
    body: dict,
    user: DispatchUser,
    context: AsyncBoltContext,
    form_data: dict,
) -> None:
    """Handles the report tactical submission"""
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
    modal = Modal(
        title="Tactical Report",
        blocks=[Section(text="Creating tactical report... Success!")],
        close="Close",
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


app.view(
    ReportTacticalActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)(ack=ack_report_tactical_submission_event, lazy=[handle_report_tactical_submission_event])


async def handle_report_executive_command(
    ack: AsyncAck,
    body: dict,
    client: AsyncWebClient,
    respond: AsyncRespond,
    context: AsyncBoltContext,
    db_session: Session,
) -> None:
    """Handles executive report command."""
    await ack()

    if context["subject"].type == "case":
        await respond(
            text="Command is not available outside of incident channels.", response_type="ephemeral"
        )
        return

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

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def ack_report_executive_submission_event(ack: AsyncAck) -> None:
    """Handles executive submission acknowledgement."""
    modal = Modal(
        title="Executive Report",
        close="Close",
        blocks=[Section(text="Creating executive report...")],
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_report_executive_submission_event(
    client: AsyncWebClient,
    body: dict,
    user: DispatchUser,
    context: AsyncBoltContext,
    form_data: dict,
) -> None:
    """Handles the report executive submission"""
    executive_report_in = ExecutiveReportCreate(
        current_status=form_data[ReportExecutiveBlockIds.current_status],
        overview=form_data[ReportExecutiveBlockIds.overview],
        next_steps=form_data[ReportExecutiveBlockIds.next_steps],
    )

    report_flows.create_executive_report(
        user_email=user.email,
        incident_id=context["subject"].id,
        executive_report_in=executive_report_in,
        organization_slug=context["subject"].organization_slug,
    )
    modal = Modal(
        title="Executive Report",
        blocks=[Section(text="Creating executive report... Success!")],
        close="Close",
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


app.view(
    ReportExecutiveActions.submit,
    middleware=[
        action_context_middleware,
        db_middleware,
        user_middleware,
        modal_submit_middleware,
        configuration_middleware,
    ],
)(ack=ack_report_executive_submission_event, lazy=[handle_report_executive_submission_event])


async def handle_update_incident_command(
    ack: AsyncAck,
    body: dict,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    db_session: Session,
) -> None:
    """Creates the incident update modal."""
    await ack()
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
            initial_options=[{"text": t.name, "value": t.name} for t in incident.tags],
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

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def ack_incident_update_submission_event(ack: AsyncAck) -> None:
    """Handles incident update submission event."""
    modal = Modal(
        title="Incident Update",
        close="Close",
        blocks=[Section(text="Updating incident...")],
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_update_incident_submission_event(
    body: dict,
    client: AsyncWebClient,
    user: DispatchUser,
    context: AsyncBoltContext,
    form_data: dict,
) -> None:
    """Handles the update incident submission"""
    # refetch session as we can't pass a db_session lazily, these could be moved to @background_task functions
    # in the future
    db_session = refetch_db_session(context["subject"].organization_slug)

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    tags = []
    for t in form_data.get(IncidentUpdateBlockIds.tags_multi_select, []):
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
    modal = Modal(
        title="Incident Update",
        close="Close",
        blocks=[Section(text="Updating incident... Success!")],
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


app.view(
    IncidentUpdateActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)(ack=ack_incident_update_submission_event, lazy=[handle_update_incident_submission_event])


async def handle_report_incident_command(
    ack: AsyncAck,
    body: dict,
    context: AsyncBoltContext,
    db_session: Session,
    client: AsyncWebClient,
) -> None:
    """Handles the report incident command."""
    await ack()

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

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


async def ack_report_incident_submission_event(ack: AsyncAck) -> None:
    """Handles the report incident submission event acknowledgment."""
    modal = Modal(
        title="Report Incident",
        close="Close",
        blocks=[Section(text="Creating incident resources...")],
    ).build()
    await ack(response_action="update", view=modal)


@handle_lazy_error
async def handle_report_incident_submission_event(
    user: DispatchUser,
    context: AsyncBoltContext,
    client: AsyncWebClient,
    body: dict,
    form_data: dict,
) -> None:
    """Handles the report incident submission"""
    # refetch session as we can't pass a db_session lazily, these could be moved to @background_task functions
    # in the future

    # TODO: handle multiple organizations during submission
    db_session = refetch_db_session(context["subject"].organization_slug)

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

    result = await client.views_update(
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

    result = await client.views_update(
        view_id=result["view"]["id"],
        hash=result["view"]["hash"],
        trigger_id=result["trigger_id"],
        view=modal,
    )

    incident_flows.incident_create_flow(
        incident_id=incident.id,
        db_session=db_session,
        organization_slug=incident.project.organization.slug,
    )


app.view(
    IncidentReportActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)(ack=ack_report_incident_submission_event, lazy=[handle_report_incident_submission_event])


@app.action(
    IncidentReportActions.project_select, middleware=[action_context_middleware, db_middleware]
)
async def handle_report_incident_project_select_action(
    ack: AsyncAck,
    body: dict,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    db_session: Session,
) -> None:
    await ack()
    values = body["view"]["state"]["values"]

    project_id = values[DefaultBlockIds.project_select][IncidentReportActions.project_select][
        "selected_option"
    ]["value"]

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

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )
