from datetime import datetime
from typing import List

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
from sqlalchemy import func

from dispatch.database.core import resolve_attr
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
from dispatch.monitor import service as monitor_service
from dispatch.nlp import build_phrase_matcher, build_term_vocab, extract_terms_from_text
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantUpdate
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.enums import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.bolt import app
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
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    command_context_middleware,
    configuration_context_middleware,
    db_middleware,
    message_context_middleware,
    modal_submit_middleware,
    user_middleware,
    restricted_command_middleware,
)
from dispatch.plugins.dispatch_slack.models import SubjectMetadata
from dispatch.plugins.dispatch_slack.service import (
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


class TaskMetadata(SubjectMetadata):
    resource_id: str


class MonitorMetadata(SubjectMetadata):
    weblink: str


def configure(config):
    """Maps commands/events to their functions."""
    middleware = [
        command_context_middleware,
        db_middleware,
        configuration_context_middleware,
        user_middleware,
    ]

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
    app.command(config.slack_command_list_incidents, middleware=middleware)(
        handle_list_incidents_command
    )
    app.command(config.slack_command_report_incident, middleware=middleware)(
        handle_report_incident_command
    )
    app.command(config.slack_command_list_resources, middleware=middleware)(
        handle_list_resources_command
    )
    app.command(config.slack_command_engage_oncall, middleware=middleware)(
        handle_engage_oncall_command
    )

    # sensitive commands
    middleware.append(restricted_command_middleware)
    app.command(config.slack_command_assign_role, middleware=middleware)(handle_assign_role_command)
    app.command(config.slack_command_update_incident, middleware=middleware)(
        handle_update_incident_command
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

    # required because allow the user to change the reaction string
    app.event(config.timeline_event_reaction, middleware=[db_middleware])(
        handle_timeline_added_event
    )


@app.options(
    DefaultActionIds.tags_multi_select, middleware=[action_context_middleware, db_middleware]
)
async def handle_tag_search_action(ack, payload, context, db_session):
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
                "value": str(
                    t.id
                ),  # NOTE slack doesn't not accept int's as values (fails silently)
            }
        )

    await ack(options=options)


@app.action(
    IncidentUpdateActions.project_select, middleware=[action_context_middleware, db_middleware]
)
async def handle_project_select_action(ack, body, client, context, db_session):
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
        Context(elements=[MarkdownText(text="Use this form to update incident details.")]),
        title_input(initial_value=incident.title),
        description_input(initial_value=incident.description),
        resolution_input(initial_value=incident.resolution),
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
        incident_priority_select(
            db_session=db_session,
            initial_option={
                "text": incident.incident_priority.name,
                "value": incident.incident_priority.id,
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
        tag_multi_select(
            optional=True,
            initial_options=[t.name for t in incident.tags],
        ),
    ]

    modal = Modal(
        title="Update Incident",
        blocks=blocks,
        submit="Submit",
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
async def handle_list_incidents_command(ack, body, respond, db_session, context):
    """Handles the list incidents command."""
    await ack()
    projects = []

    if context["subject"].type == "incident":
        # command was run in an incident conversation
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        projects.append(incident.project)
    else:
        # command was run in a non-incident conversation
        args = body["command"]["text"].split(" ")

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

    blocks = [Context(text="Incident List")]

    if incidents:
        for incident in incidents:
            if incident.visibility == Visibility.open:
                blocks.append(
                    Section(
                        fields=[
                            f"*<{incident.ticket.weblink}|{incident.name}>*",
                            f"*Title*:\n {incident.title}",
                            f"*Type*:\n {incident.incident_type.name}",
                            f"*Severity*:\n {incident.incident_severity.name}",
                            f"*Priority*:\n {incident.incident_priority.name}",
                            f"*Status*:\n{incident.status}",
                            f"*Incident Commander*:\n<{incident.commander.individual.weblink}|{incident.commander.individual.name}>",
                            f"*Project*:\n{incident.project.name}",
                        ]
                    )
                )

    blocks = Message(blocks=blocks).build()["blocks"]
    await respond(text="Incident List", blocks=blocks, response_type="ephemeral")


async def handle_list_participants_command(ack, body, respond, client, db_session, context):
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


async def handle_list_tasks_command(ack, user, body, respond, context, db_session):
    """Handles the list tasks command."""
    await ack()
    blocks = []

    caller_only = False
    # if body["command"] == context["config"].slack_command_list_my_tasks:
    #    caller_only = True

    for status in TaskStatus:
        blocks.append(Section(text=f"*{status} Incident Tasks*"))
        button_text = "Resolve" if status == TaskStatus.open else "Re-open"

        tasks = task_service.get_all_by_incident_id_and_status(
            db_session=db_session, incident_id=context["subject"].id, status=status
        )

        if caller_only:
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


async def handle_list_resources_command(ack, body, respond, client, db_session, context, logger):
    """Handles the list resources command."""
    await ack()
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    incident_description = (
        incident.description
        if len(incident.description) <= 500
        else f"{incident.description[:500]}..."
    )

    blocks = [
        Section(text=f"*<{incident.title}|https://google.com>*"),
        Section(text=f"*Description* \n {incident_description}"),
        Section(
            text=f"*Commander* \n <{incident.commander.individual.weblink}|{incident.commander.individual.name}>"
        ),
        Section(
            text=f"*Reporter* \n <{incident.reporter.individual.weblink}|{incident.reporter.individual.name}>"
        ),
    ]

    if resolve_attr(incident, "incident_document.weblink"):
        blocks.append(Section(text=f"*<{incident.incident_document.weblink}|Incident Document>*"))

    if resolve_attr(incident, "storage.weblink"):
        blocks.append(Section(text=f"*<{incident.storage.weblink}|Storage>*"))

    if resolve_attr(incident, "ticket.weblink"):
        blocks.append(Section(text=f"*<{incident.ticket.weblink}|Ticket>*"))

    if resolve_attr(incident, "conference.weblink"):
        blocks.append(Section(text=f"*<{incident.conference.weblink}|Conference>*"))

    if resolve_attr(incident, "incident_review_document"):
        blocks.append(
            Section(text=f"*<{incident.incident_review_document}|Incident Review Document>(")
        )

    faq_doc = document_service.get_incident_faq_document(
        db_session=db_session, project_id=incident.project_id
    )
    if faq_doc:
        blocks.append(Section(text=f"*<{faq_doc.weblink}|FAQ Document>*"))

    conversation_reference = document_service.get_conversation_reference_document(
        db_session=db_session, project_id=incident.project_id
    )
    if conversation_reference:
        blocks.append(Section(text=f"*<{conversation_reference.weblink}|Command Reference>*"))

    blocks = Message(blocks=blocks).build()["blocks"]
    await respond(text="Incident Resources Message", blocks=blocks, response_type="ephemeral")


# EVENTS


async def handle_timeline_added_event(ack, body, client, context, db_session):
    """Handles an event where a reaction is added to a message."""
    conversation_id = context["channel_id"]
    message_ts = context["ts"]
    message_ts_utc = datetime.datetime.utcfromtimestamp(float(message_ts))

    # we fetch the message information
    response = dispatch_slack_service.list_conversation_messages(
        client, conversation_id, latest=message_ts, limit=1, inclusive=1
    )
    message_text = response["messages"][0]["text"]
    message_sender_id = response["messages"][0]["user"]

    # TODO handle case reactions
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


@app.event(
    {"type": "message"}, middleware=[message_context_middleware, db_middleware, user_middleware]
)
async def handle_participant_role_activity(ack, db_session, context, user):
    """Increments the participant role's activity counter."""
    await ack()

    # TODO add when case support when participants are added.
    if context["subject"].type == "incident":
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=user.email
        )

        if participant:
            active_participant_roles = participant.active_roles
            for participant_role in active_participant_roles:
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


@app.event(
    {"type": "message"}, middleware=[message_context_middleware, user_middleware, db_middleware]
)
async def handle_after_hours_message(ack, context, body, client, respond, user, db_session):
    """Notifies the user that this incident is current in after hours mode."""
    # we ignore user channel and group join messages
    await ack()

    if body["subtype"] in ["channel_join", "group_join"]:
        return

    if context["subject"].type == "case":
        return

    # get their timezone from slack
    elif context["subject"].type == "incident":
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        owner_email = incident.commander.individual.email
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=user.email
        )

        # get their timezone from slack
        owner_tz = dispatch_slack_service.get_user_info_by_email(client, email=owner_email)["tz"]

        message = f"Responses may be delayed. The current incident priority is *{incident.incident_priority.name}* and your message was sent outside of the Incident Commander's working hours (Weekdays, 9am-5pm, {owner_tz} timezone)."

    now = datetime.datetime.now(pytz.timezone(owner_tz))
    is_business_hours = now.weekday() not in [5, 6] and 9 <= now.hour < 17

    if not is_business_hours:
        if not participant.after_hours_notification:
            blocks = [Section(text=message)]
            participant.after_hours_notification = True
            db_session.add(participant)
            db_session.commit()
            blocks = Message(blocks=blocks).build()["blocks"]
            await respond(blocks=blocks, response_type="ephemeral")


@app.event("member_joined", middleware=[action_context_middleware, user_middleware, db_middleware])
async def handle_member_joined_channel(ack, user, body, client, db_session, context):
    """Handles the member_joined_channel Slack event."""
    await ack()
    participant = incident_flows.incident_add_or_reactivate_participant_flow(
        user_email=user.email, incident_id=context["subject"].id, db_session=db_session
    )

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    if body["inviter"]:
        inviter_email = await get_user_email_async(client=client, user_id=body["inviter"])
        client.user
        added_by_participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=inviter_email
        )
        participant.added_by = added_by_participant
        participant.added_reason = body["text"]
    else:
        participant.added_by = incident.commander
        participant.added_reason = f"Participant added by {added_by_participant.individual.name}"

    db_session.add(participant)
    db_session.commit()


@app.event("member_left", middleware=[action_context_middleware, db_middleware])
async def handle_member_left_channel(ack, context, db_session, user):
    await ack()
    incident_flows.incident_remove_participant_flow(
        user.email, context["subject"].id, db_session=db_session
    )


@app.event(
    {"type": "message", "subtype": "message_replied"}, middleware=[action_context_middleware]
)
async def handle_thread_creation(ack, respond, client, context):
    """Sends the user an ephemeral message if they use threads."""
    # if not context["config"].ban_threads:
    #    return

    message = "Please refrain from using threads in incident related channels. Threads make it harder for incident participants to maintain context."
    await respond(text=message, response_type="ephemeral")


@app.event({"type": "message"}, middleware=[message_context_middleware, db_middleware])
async def handle_message_tagging(ack, db_session, context):
    """Looks for incident tags in incident messages."""

    # TODO handle case tagging
    if context["subject"].type == "incident":
        text = context["text"]
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


@app.event({"type": "message"}, middleware=[message_context_middleware, db_middleware])
async def handle_message_monitor(ack, respond, body, context, db_session):
    """Looks strings that are available for monitoring (usually links)."""
    await ack()
    # TODO handle cases
    if context["subject"].type == "incident":
        incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
        project_id = incident.project.id
        button_metadata = MonitorMetadata(
            type="incident",
            organization_slug=incident.project.organization.slug,
            id=incident.id,
            project_id=incident.project.id,
            channel_id=context["channel_id"],
        )

    else:
        return

    plugins = plugin_service.get_active_instances(
        db_session=db_session, project_id=project_id, plugin_type="monitor"
    )

    for p in plugins:
        for matcher in p.instance.get_matchers():
            for match in matcher.finditer(body["text"]):
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

                    button_metadata.weblink = match_data["weblink"]

                    blocks = [
                        Section(
                            text="Hi! Dispatch is able to help track the status of: \n {match_data['weblink']} \n\n Would you like for changes in it's status to be propagated to this incident channel?"
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
                    await respond(blocks=blocks, response_type="ephemeral")


# MODALS
async def handle_add_timeline_event_command(ack, body, client, context):
    """Handles the add timeline event command."""
    await ack()
    blocks = [
        Context(
            elements=[MarkdownText(text="Use this form to add an event to the incident timeline.")]
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


@app.view(
    AddTimelineEventActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_add_timeline_submission_event(ack, user, client, context, db_session, form_data):
    """Handles the add timeline submission event."""
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

    blocks = [Section(text="Success!")]

    modal = Modal(
        title="Timeline Event Added",
        close="Close",
        blocks=blocks,
        private_metadata=context["subject"].json(),
    ).build()

    await ack(response_action="update", view=modal)


async def handle_update_participant_command(ack, respond, body, context, db_session, client):
    """Handles the update participant command."""
    await ack()
    if context["subject"].type == "case":
        await respond(text="This command is not yet supported in the case context.")

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
        submit="Submit",
        close="Cancel",
        callback_id=UpdateParticipantActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    UpdateParticipantActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_update_participant_submission_event(
    ack, user, client, context, db_session, form_data
):
    """Handles the update participant submission event."""
    ack()


async def handle_update_notifications_group_command(ack, body, context, client, db_session):
    """Handles the update notification group command."""
    await ack()

    # TODO handle cases
    if context["subject"].type == "case":
        return

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    group_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=incident.project.id, plugin_type="participant-group"
    )
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
                text=", ".join(members),
                multiline=True,
                action_id=UpdateNotificationGroupActionIds.members,
            ),
            block_id=UpdateNotificationGroupBlockIds.members,
        ),
        Context(elements=MarkdownText(text="Separate email addresses with commas")),
    ]

    modal = Modal(
        title="Update Group Membership",
        blocks=blocks,
        close="Cancel",
        submit="Submit",
        callback_id=UpdateNotificationGroupActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    UpdateNotificationGroupActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_update_notifications_group_submission_event(
    ack, user, client, context, db_session, form_data
):
    """Handles the update notifications group submission"""
    ack()


async def handle_assign_role_command(ack, context, body, client):
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
                    text="Assign a role to a participant. Note: User will be invited to incident channel if they are not yet a member."
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


@app.view(
    AssignRoleActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_assign_role_submission_event(ack, user, client, context, db_session, form_data):
    """Handles the assign role submission."""
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
        or assignee_role == ParticipantRoleType.incident_commander
    ):
        # we update the external ticket
        incident_flows.update_external_incident_ticket(
            incident_id=context["subject"].id, db_session=db_session
        )

    modal = Modal(title="Engagement", blocks=[Section(text="Success!")], close="Close").build()
    await ack(response_action="update", view=modal)


async def handle_engage_oncall_command(ack, respond, context, body, client, db_session):
    """Handles the engage oncall command."""
    await ack()
    # TODO handle cases
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


@app.view(
    EngageOncallActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_engage_oncall_submission_event(ack, user, context, db_session, form_data):
    """Handles the engage oncall submission"""
    await ack()

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
    await ack(response_action="update", view=modal)


async def handle_report_tactical_command(ack, client, respond, context, db_session, body):
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
        submit="Submit",
        close="Close",
        callback_id=ReportTacticalActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    ReportTacticalActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_report_tactical_submission_event(
    ack, user, client, context, db_session, form_data
):
    """Handles the report tactical submission"""
    await ack()

    tactical_report_in = TacticalReportCreate(
        conditions=form_data[ReportTacticalBlockIds.conditions],
        actions=form_data[ReportTacticalBlockIds.actions],
        needs=form_data[ReportTacticalBlockIds.needs],
    )

    report_flows.create_tactical_report(
        user_email=user.email,
        incident_id=context["subject"].id,
        tactical_report_in=tactical_report_in,
        db_session=db_session,
    )


async def handle_report_executive_command(ack, body, client, respond, context, db_session):
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
                placeholder="Current incident status", initial_value=current_status, multiline=True
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
                placeholder="Current incident needs", initial_value=next_steps, multiline=True
            ),
            block_id=ReportExecutiveBlockIds.next_steps,
        ),
        # Context(
        #    elements=[
        #        MarkdownText(
        #            text=f"Use {context['config'].slack_command_update_notifications_group} to update the list of recipients of this report."
        #        )
        #    ]
        # ),
    ]

    modal = Modal(
        title="Executive Report",
        blocks=blocks,
        submit="Submit",
        close="Close",
        callback_id=ReportExecutiveActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    ReportExecutiveActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_report_executive_submission_event(
    user, client, body, context, db_session, form_data
):
    """Handles the report executive submission"""
    executive_report_in = ExecutiveReportCreate(
        current_status=form_data[ReportExecutiveBlockIds.current_status],
        overview=form_data[ReportExecutiveBlockIds.overview],
        next_steps=form_data[ReportExecutiveBlockIds.next_steps],
    )

    modal = Modal(
        title="Executive Report",
        close="Close",
        blocks=[Section(text="Creating report and sending it to recipients...")],
    ).build()

    stack = await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )

    report_flows.create_executive_report(
        user_email=user.email,
        incident_id=context["subject"].id,
        executive_report_in=executive_report_in,
        db_session=db_session,
    )

    modal = Modal(
        title="Executive Report",
        close="Close",
        blocks=[Section(text="Creating report and sending it to recipients... Success!")],
    ).build()

    await client.views_update(
        view_id=stack["view"]["id"],
        hash=stack["view"]["hash"],
        trigger_id=stack["trigger_id"],
        view=modal,
    )


async def handle_update_incident_command(ack, body, client, context, db_session):
    """Creates the incident update modal."""
    await ack()
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    blocks = [
        Context(elements=[MarkdownText(text="Use this form to update incident details.")]),
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
        incident_priority_select(
            db_session=db_session,
            initial_option={
                "text": incident.incident_priority.name,
                "value": incident.incident_priority.id,
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
        tag_multi_select(
            optional=True,
            initial_options=[{"text": t.name, "value": t.name} for t in incident.tags],
        ),
    ]

    modal = Modal(
        title="Update Incident",
        blocks=blocks,
        submit="Submit",
        close="Cancel",
        callback_id=IncidentUpdateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    IncidentUpdateActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_update_incident_submission_event(
    ack, body, client, user, context, db_session, form_data
):
    """Handles the update incident submission"""
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

    modal = Modal(
        title="Incident Update",
        close="Close",
        blocks=[Section(text="The incident is being updated...")],
    ).build()

    stack = await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
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
        blocks=[Section(text="The incident has been successfully updated!")],
    ).build()

    await client.views_update(
        view_id=stack["view"]["id"],
        hash=stack["view"]["hash"],
        trigger_id=stack["trigger_id"],
        view=modal,
    )


async def handle_report_incident_command(ack, body, context, db_session, client):
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
        submit="Submit",
        close="Cancel",
        callback_id=IncidentReportActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    IncidentReportActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_report_incident_submission_event(ack, user, client, body, db_session, form_data):
    """Handles the report incident submission"""
    await ack()
    tags = []
    for t in form_data.get(DefaultBlockIds.tags_multi_select, []):
        # we have to fetch as only the IDs are embedded in slack
        tag = tag_service.get(db_session=db_session, tag_id=int(t["value"]))
        tags.append(tag)

    project = {"name": form_data[DefaultBlockIds.project_select]["name"]}
    incident_in = IncidentCreate(
        title=form_data[DefaultBlockIds.title_input],
        description=form_data[DefaultBlockIds.description_input],
        incident_type={"name": form_data[DefaultBlockIds.incident_type_select]["name"]},
        incident_priority={"name": form_data[DefaultBlockIds.incident_priority_select]["name"]},
        project=project,
        reporter=ParticipantUpdate(individual=IndividualContactRead(email=user.email)),
        tags=tags,
    )

    # Create the incident
    incident = incident_service.create(db_session=db_session, incident_in=incident_in)

    blocks = [
        Section(
            text="This is a confirmation that you have reported a incident with the following information. You will be invited to an incident slack conversation shortly."
        ),
        Section(text=f"*Incident Title*\n {incident.title}"),
        Section(text=f"*Description*\n {incident.description}"),
        Section(
            fields=[
                MarkdownText(text=f"*Commander* \n {incident.commander.individual.name}"),
                MarkdownText(text=f"*Type*\n {incident.incident_type.name}"),
                MarkdownText(text=f"*Severity*\n {incident.incident_severity.name}"),
                MarkdownText(text=f"*Priority*\n {incident.incident_priority.name}"),
            ]
        ),
    ]

    modal = Modal(title="Incident Report", blocks=blocks, close="Close").build()

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
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
async def handle_report_incident_project_select_action(ack, body, client, context, db_session):
    await ack()
    values = body["view"]["state"]["values"]

    project_id = values[DefaultBlockIds.project_select][IncidentReportActions.project_select][
        "selected_option"
    ]["value"]

    project = project_service.get(db_session=db_session, project_id=project_id)

    blocks = [
        Context(elements=[MarkdownText(text="Use this form to update incident details.")]),
        title_input(),
        description_input(),
        project_select(
            db_session=db_session,
            action_id=IncidentReportActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(db_session=db_session, project_id=project.id, optional=True),
        incident_priority_select(db_session=db_session, project_id=project.id, optional=True),
        incident_severity_select(db_session=db_session, project_id=project.id, optional=True),
        tag_multi_select(optional=True),
    ]

    modal = Modal(
        title="Report Incident",
        blocks=blocks,
        submit="Submit",
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
