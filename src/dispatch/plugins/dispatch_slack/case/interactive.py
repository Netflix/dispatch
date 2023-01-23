from blockkit import Context, Input, MarkdownText, Modal, Section, UsersSelect

from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.enums import CaseStatus
from dispatch.case.models import CaseCreate, CaseUpdate
from dispatch.incident import flows as incident_flows
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseEscalateActions,
    CaseNotificationActions,
    CaseReportActions,
    CaseResolveActions,
    CaseShortcutCallbacks,
)
from dispatch.plugins.dispatch_slack.case.messages import (
    create_case_message,
)
from dispatch.plugins.dispatch_slack.fields import (
    DefaultBlockIds,
    case_priority_select,
    case_status_select,
    case_type_select,
    description_input,
    incident_priority_select,
    incident_type_select,
    project_select,
    resolution_input,
    title_input,
)
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    button_context_middleware,
    db_middleware,
    modal_submit_middleware,
    shortcut_context_middleware,
    user_middleware,
)
from dispatch.project import service as project_service


def configure(config):
    """Maps commands/events to their functions."""
    pass


def assignee_select(
    placeholder: str = "Select Assignee",
    initial_user: str = None,
    action_id: str = None,
    block_id: str = None,
    label: str = "Assignee",
    **kwargs,
):
    """Builds a assignee select block."""
    return Input(
        element=UsersSelect(
            placeholder=placeholder, action_id=action_id, initial_user=initial_user
        ),
        block_id=block_id,
        label=label,
        **kwargs,
    )


@app.action(CaseNotificationActions.reopen, middleware=[button_context_middleware, db_middleware])
async def reopen_button_click(
    ack,
    client,
    context,
    db_session,
):
    await ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    case.status = CaseStatus.triage
    db_session.commit()

    # update case message
    blocks = create_case_message(case=case, channel_id=context["subject"].channel_id)
    await client.chat_update(
        blocks=blocks, ts=case.conversation.thread_id, channel=case.conversation.channel_id
    )


@app.action(
    CaseNotificationActions.escalate,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
async def escalate_button_click(
    ack,
    body,
    client,
    context,
    db_session,
):
    await ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    blocks = [
        Context(elements=[MarkdownText(text="Accept the defaults or adjust as needed.")]),
        title_input(initial_value=case.title),
        description_input(initial_value=case.description),
        project_select(
            db_session=db_session,
            initial_option={"text": case.project.name, "value": case.project.id},
            action_id=CaseEscalateActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(
            db_session=db_session,
            initial_option={
                "text": case.case_type.incident_type.name,
                "value": case.case_type.incident_type.id,
            },
            project_id=case.project.id,
        ),
        incident_priority_select(db_session=db_session, project_id=case.project.id, optional=True),
    ]

    modal = Modal(
        title="Escalate Case",
        blocks=blocks,
        submit="Escalate",
        close="Close",
        callback_id=CaseEscalateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.action(
    CaseEscalateActions.project_select, middleware=[action_context_middleware, db_middleware]
)
async def handle_project_select_action(
    ack,
    body,
    client,
    context,
    db_session,
):
    await ack()
    values = body["view"]["state"]["values"]

    project_id = values[DefaultBlockIds.project_select][CaseEscalateActions.project_select][
        "selected_option"
    ]["value"]

    project = project_service.get(db_session=db_session, project_id=project_id)

    blocks = [
        Context(elements=[MarkdownText(text="Accept the defaults or adjust as needed.")]),
        title_input(),
        description_input(),
        assignee_select(),
        project_select(
            db_session=db_session,
            initial_option={"text": project.name, "value": project.id},
            action_id=CaseEscalateActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(
            db_session=db_session, initial_option=None, project_id=project.id, block_id=None
        ),
        incident_priority_select(
            db_session=db_session,
            project_id=project.id,
            initial_option=None,
            optional=True,
            block_id=None,  # ensures state is reset
        ),
    ]

    modal = Modal(
        title="Escalate Case",
        blocks=blocks,
        submit="Submit",
        close="Close",
        callback_id=CaseEscalateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


@app.view(CaseEscalateActions.submit, middleware=[action_context_middleware, db_middleware])
async def handle_escalation_submission_event(
    ack,
    client,
    context,
    db_session,
    user,
):
    await ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    case.status = CaseStatus.escalated
    db_session.commit()

    blocks = create_case_message(case=case, channel_id=context["subject"].channel_id)
    await client.chat_update(
        blocks=blocks, ts=case.conversation.thread_id, channel=case.conversation.channel_id
    )
    await client.chat_postMessage(
        text="This case has been escalated to an incident. All further triage work will take place in the incident channel.",
        channel=case.conversation.channel_id,
        thread_ts=case.conversation.thread_id,
    )
    incident = case_flows.case_escalated_status_flow(
        case=case, organization_slug=context["subject"].organization_slug, db_session=db_session
    )

    incident_flows.add_participants_to_conversation(
        db_session=db_session, participant_emails=[user.email], incident=incident
    )


@app.action(
    CaseNotificationActions.join_incident,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
async def join_incident_button_click(ack, body, user, db_session, context, client):
    await ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    # TODO handle case there are multiple related incidents
    incident_flows.add_participants_to_conversation(
        db_session=db_session, participant_emails=[user.email], incident=case.incidents[0]
    )


@app.action(CaseNotificationActions.edit, middleware=[button_context_middleware, db_middleware])
async def edit_button_click(ack, body, db_session, context, client):
    await ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    assignee_initial_user = (await client.users_lookupByEmail(email=case.assignee.email))["user"][
        "id"
    ]

    blocks = [
        title_input(initial_value=case.title),
        description_input(initial_value=case.description),
        resolution_input(initial_value=case.resolution),
        assignee_select(initial_user=assignee_initial_user),
        case_status_select(initial_option={"text": case.status, "value": case.status}),
        case_type_select(
            db_session=db_session,
            initial_option={"text": case.case_type.name, "value": case.case_type.id},
            project_id=case.project.id,
        ),
        case_priority_select(
            db_session=db_session,
            initial_option={"text": case.case_priority.name, "value": case.case_priority.id},
            project_id=case.project.id,
            optional=True,
        ),
    ]

    modal = Modal(
        title="Edit Case",
        blocks=blocks,
        submit="Update",
        close="Close",
        callback_id=CaseResolveActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.action(CaseNotificationActions.resolve, middleware=[button_context_middleware, db_middleware])
async def resolve_button_click(ack, body, db_session, context, client):
    await ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    assignee_initial_user = (await client.users_lookupByEmail(email=case.assignee.email))["user"][
        "id"
    ]
    blocks = [
        Context(elements=[MarkdownText(text="Accept the defaults or adjust as needed.")]),
        title_input(initial_value=case.title),
        description_input(initial_value=case.description),
        resolution_input(initial_value=case.resolution),
        assignee_select(initial_user=assignee_initial_user),
        case_type_select(
            db_session=db_session,
            initial_option={"text": case.case_type.name, "value": case.case_type.id},
            project_id=case.project.id,
        ),
        case_priority_select(
            db_session=db_session,
            initial_option={"text": case.case_priority.name, "value": case.case_priority.id},
            project_id=case.project.id,
            optional=True,
        ),
    ]

    modal = Modal(
        title="Resolve Case",
        blocks=blocks,
        submit="Resolve",
        close="Close",
        callback_id=CaseResolveActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    CaseResolveActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_resolve_submission_event(
    ack, body, context, payload, user, form_data, db_session, client
):
    await ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    case_priority = None
    if form_data.get(DefaultBlockIds.case_priority_select):
        case_priority = {"name": form_data[DefaultBlockIds.case_priority_select]["name"]}

    case_type = None
    if form_data.get(DefaultBlockIds.case_type_select):
        case_type = {"name": form_data[DefaultBlockIds.case_type_select]["name"]}

    case_in = CaseUpdate(
        title=form_data[DefaultBlockIds.title_input],
        description=form_data[DefaultBlockIds.description_input],
        resolution=form_data[DefaultBlockIds.resolution_input],
        status=CaseStatus.closed,
        visibility=case.visibility,
        case_priority=case_priority,
        case_type=case_type,
    )

    case = case_service.update(db_session=db_session, case=case, case_in=case_in, current_user=user)
    blocks = create_case_message(case=case, channel_id=context["subject"].channel_id)
    await client.chat_update(
        blocks=blocks, ts=case.conversation.thread_id, channel=case.conversation.channel_id
    )


@app.shortcut(CaseShortcutCallbacks.report, middleware=[db_middleware, shortcut_context_middleware])
async def report_issue(ack, shortcut, body, context, db_session, client):
    await ack()
    initial_description = None
    if body.get("message"):
        permalink = (
            await client.chat_getPermalink(
                channel=context["subject"].channel_id, message_ts=body["message"]["ts"]
            )
        )["permalink"]
        initial_description = f"{body['message']['text']}\n\n{permalink}"

    blocks = [
        Context(
            elements=[
                MarkdownText(text="Fill the following form out to the best of your abilities.")
            ]
        ),
        title_input(),
        description_input(initial_value=initial_description),
        project_select(
            db_session=db_session,
            action_id=CaseReportActions.project_select,
            dispatch_action=True,
        ),
    ]

    modal = Modal(
        title="Report Issue",
        blocks=blocks,
        submit="Report",
        close="Close",
        callback_id=CaseReportActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    await client.views_open(trigger_id=shortcut["trigger_id"], view=modal)


@app.action(CaseReportActions.project_select, middleware=[db_middleware, action_context_middleware])
async def handle_report_project_select_action(ack, body, db_session, context, client):
    await ack()
    values = body["view"]["state"]["values"]

    project_id = values[DefaultBlockIds.project_select][CaseReportActions.project_select][
        "selected_option"
    ]["value"]

    project = project_service.get(
        db_session=db_session,
        project_id=project_id,
    )

    blocks = [
        Context(elements=[MarkdownText(text="Accept the defaults or adjust as needed.")]),
        title_input(),
        description_input(),
        project_select(
            db_session=db_session,
            initial_option={"text": project.name, "value": project.id},
            action_id=CaseReportActions.project_select,
            dispatch_action=True,
        ),
        case_type_select(
            db_session=db_session, initial_option=None, project_id=project.id
        ),
        case_priority_select(
            db_session=db_session,
            project_id=project.id,
            initial_option=None,
            optional=True,
            block_id=None,  # ensures state is reset
        ),
    ]

    modal = Modal(
        title="Report Issue",
        blocks=blocks,
        submit="Report",
        close="Close",
        callback_id=CaseReportActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


@app.view(
    CaseReportActions.submit,
    middleware=[db_middleware, action_context_middleware, modal_submit_middleware, user_middleware],
)
async def handle_report_submission_event(
    ack, body, context, form_data, db_session, user, client, logger
):
    await ack()

    case_priority = None
    if form_data.get(DefaultBlockIds.case_priority_select):
        case_priority = {"name": form_data[DefaultBlockIds.case_priority_select]["name"]}

    case_type = None
    if form_data.get(DefaultBlockIds.case_type_select):
        case_type = {"name": form_data[DefaultBlockIds.case_type_select]["name"]}

    case_in = CaseCreate(
        title=form_data[DefaultBlockIds.title_input],
        description=form_data[DefaultBlockIds.description_input],
        status=CaseStatus.new,
        case_priority=case_priority,
        case_type=case_type,
    )

    case = case_service.create(db_session=db_session, case_in=case_in, current_user=user)

    modal = Modal(
        title="Case Created",
        close="Close",
        blocks=[Section(text="Your case has been created. Running case execution flows now...")],
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )

    case_flows.case_new_create_flow(
        case_id=case.id, organization_slug=context["subject"].organization_slug
    )

    modal = Modal(
        title="Case Created",
        close="Close",
        blocks=[Section(text="Your case has been created.")],
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )
