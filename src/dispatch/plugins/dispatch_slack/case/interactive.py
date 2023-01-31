import re
from datetime import datetime

import pytz
from blockkit import Context, Input, MarkdownText, Modal, Section, UsersSelect
from slack_bolt import Ack, BoltContext
from slack_sdk.web.client import WebClient
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.enums import CaseStatus
from dispatch.case.models import CaseCreate, CaseUpdate
from dispatch.incident import flows as incident_flows
from dispatch.participant import service as participant_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseEscalateActions,
    CaseNotificationActions,
    CaseReportActions,
    CaseResolveActions,
    CaseShortcutCallbacks,
)
from dispatch.plugins.dispatch_slack.case.messages import create_case_message
from dispatch.plugins.dispatch_slack.decorators import message_dispatcher
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
from dispatch.plugins.dispatch_slack.service import get_user_email
from dispatch.project import service as project_service


def configure(config):
    """Maps commands/events to their functions."""
    return


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


@message_dispatcher.add(
    exclude={"subtype": ["channel_join", "channel_leave"]}
)  # we ignore channel join and leave messages
def handle_new_participant_added(ack: Ack, context: BoltContext, client: WebClient) -> None:
    """Looks for new participants being added to conversation via @<user-name>"""
    ack()
    if context["subject"].type == "case":
        participants = re.findall(context["message"], r"\<\@([a-zA-Z0-9]*)\>")
        for user_id in participants:
            user_email = get_user_email(client=client, user_id=user_id)

            participant = case_flows.case_add_or_reactivate_participant_flow(
                case_id=context["subject"].id, user_email=user_email
            )
            participant.user_conversation_id = user_id


@message_dispatcher.add(
    exclude={"subtype": ["channel_join", "channel_leave"]}
)  # we ignore channel join and leave messages
def handle_participant_role_activity(
    ack: Ack, db_session: Session, context: BoltContext, user: DispatchUser
) -> None:
    ack()
    if context["subject"].type == "case":
        participant = participant_service.get_by_case_id_and_email(
            db_session=db_session, case_id=context["subject"].id, email=user.email
        )

        if participant:
            for participant_role in participant.active_roles:
                participant_role.activity += 1
        else:
            # we have a new active participant lets add them
            participant = case_flows.case_add_or_reactivate_participant_flow(
                case_id=context["subject"].id, user_email=user.email
            )
            participant.user_conversation_id = context["user_id"]
        db_session.commit()


@message_dispatcher.add(
    exclude={"subtype": ["channel_join", "group_join"]}
)  # we ignore user channel and group join messages
def handle_after_hours_message(
    ack: Ack,
    context: BoltContext,
    client: WebClient,
    db_session: Session,
    payload: dict,
    user: DispatchUser,
) -> None:
    """Notifies the user that this case is currently in after hours mode."""
    ack()

    if context["subject"].type == "case":
        case = case_service.get(db_session=db_session, case_id=context["subject"].id)
        owner_email = case.assignee.individual.email
        participant = participant_service.get_by_case_id_and_email(
            db_session=db_session, case_id=context["subject"].id, email=user.email
        )
        # get their timezone from slack
        owner_tz = (dispatch_slack_service.get_user_info_by_email(client, email=owner_email))["tz"]
        message = f"Responses may be delayed. The current case priority is *{case.case_priority.name}* and your message was sent outside of the Assignee's working hours (Weekdays, 9am-5pm, {owner_tz} timezone)."

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
                thread_is=payload["thread_ts"],
                user=payload["user"],
            )


@app.action("button-link")
def ack_button_link(ack: Ack):
    """Handles noop button link action."""
    ack()


@app.action(CaseNotificationActions.reopen, middleware=[button_context_middleware, db_middleware])
def reopen_button_click(
    ack: Ack,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    case.status = CaseStatus.triage
    db_session.commit()

    # update case message
    blocks = create_case_message(case=case, channel_id=context["subject"].channel_id)
    client.chat_update(
        blocks=blocks, ts=case.conversation.thread_id, channel=case.conversation.channel_id
    )


@app.action(
    CaseNotificationActions.escalate,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
def escalate_button_click(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
):
    ack()
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
    client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.action(
    CaseEscalateActions.project_select, middleware=[action_context_middleware, db_middleware]
)
def handle_project_select_action(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
):
    ack()
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

    client.views_update(
        view_id=body["view"]["id"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


def ack_handle_escalation_submission_event(ack: Ack) -> None:
    """Handles the escalation submission event."""
    modal = Modal(
        title="Escalate Case",
        close="Close",
        blocks=[Section(text="Escalating case as incident...")],
    ).build()
    ack(response_action="update", view=modal)


def handle_escalation_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    user: DispatchUser,
):
    """Handles the escalation submission event."""
    ack_handle_escalation_submission_event(ack=ack)

    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    case.status = CaseStatus.escalated
    db_session.commit()

    blocks = create_case_message(case=case, channel_id=context["subject"].channel_id)
    client.chat_update(
        blocks=blocks, ts=case.conversation.thread_id, channel=case.conversation.channel_id
    )
    client.chat_postMessage(
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

    modal = Modal(
        title="Escalate Case",
        close="Close",
        blocks=blocks,
    ).build()

    client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


app.view(CaseEscalateActions.submit, middleware=[action_context_middleware, db_middleware])(
    ack=ack_handle_escalation_submission_event, lazy=[handle_escalation_submission_event]
)


@app.action(
    CaseNotificationActions.join_incident,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
def join_incident_button_click(
    ack: Ack, user: DispatchUser, db_session: Session, context: BoltContext
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    # TODO handle case there are multiple related incidents
    incident_flows.add_participants_to_conversation(
        db_session=db_session, participant_emails=[user.email], incident=case.incidents[0]
    )


@app.action(CaseNotificationActions.edit, middleware=[button_context_middleware, db_middleware])
def edit_button_click(
    ack: Ack, body: dict, db_session: Session, context: BoltContext, client: WebClient
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    assignee_initial_user = client.users_lookupByEmail(email=case.assignee.individual.email)[
        "user"
    ]["id"]

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
    client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.action(CaseNotificationActions.edit, middleware=[button_context_middleware, db_middleware])
def handle_edit_submission_event(
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
):
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
        status=form_data[DefaultBlockIds.case_status_select],
        visibility=case.visibility,
        case_priority=case_priority,
        case_type=case_type,
    )

    case = case_service.update(db_session=db_session, case=case, case_in=case_in, current_user=user)
    blocks = create_case_message(case=case, channel_id=context["subject"].channel_id)
    client.chat_update(
        blocks=blocks, ts=case.conversation.thread_id, channel=case.conversation.channel_id
    )


@app.action(CaseNotificationActions.resolve, middleware=[button_context_middleware, db_middleware])
def resolve_button_click(
    ack: Ack, body: dict, db_session: Session, context: BoltContext, client: WebClient
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    blocks = [
        resolution_input(initial_value=case.resolution),
    ]

    modal = Modal(
        title="Resolve Case",
        blocks=blocks,
        submit="Resolve",
        close="Close",
        callback_id=CaseResolveActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    CaseResolveActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_resolve_submission_event(
    ack: Ack,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    case_in = CaseUpdate(
        title=case.title,
        resolution=form_data[DefaultBlockIds.resolution_input],
        visibility=case.visibility,
        status=CaseStatus.closed,
    )

    case = case_service.update(db_session=db_session, case=case, case_in=case_in, current_user=user)
    blocks = create_case_message(case=case, channel_id=context["subject"].channel_id)
    client.chat_update(
        blocks=blocks, ts=case.conversation.thread_id, channel=case.conversation.channel_id
    )


@app.shortcut(CaseShortcutCallbacks.report, middleware=[db_middleware, shortcut_context_middleware])
def report_issue(
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
    client.views_open(trigger_id=shortcut["trigger_id"], view=modal)


@app.action(CaseReportActions.project_select, middleware=[db_middleware, action_context_middleware])
def handle_report_project_select_action(
    ack: Ack, body: dict, db_session: Session, context: BoltContext, client: WebClient
):
    ack()
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
        case_type_select(db_session=db_session, initial_option=None, project_id=project.id),
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

    client.views_update(
        view_id=body["view"]["id"],
        trigger_id=body["trigger_id"],
        view=modal,
    )


@app.view(
    CaseReportActions.submit,
    middleware=[db_middleware, action_context_middleware, modal_submit_middleware, user_middleware],
)
def handle_report_submission_event(
    ack: Ack,
    body: dict,
    context: BoltContext,
    form_data: dict,
    db_session: Session,
    user: DispatchUser,
    client: WebClient,
):
    ack()

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

    result = client.views_update(
        view_id=body["view"]["id"],
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

    client.views_update(
        view_id=result["view"]["id"],
        trigger_id=result["trigger_id"],
        view=modal,
    )
