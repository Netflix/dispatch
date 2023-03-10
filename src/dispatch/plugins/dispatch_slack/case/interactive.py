import json
import re
from datetime import datetime, timedelta

import pytz
from blockkit import (
    Actions,
    Button,
    Context,
    Divider,
    Input,
    MarkdownText,
    Modal,
    Section,
    UsersSelect,
)
from slack_bolt import Ack, BoltContext, Respond
from slack_sdk.web.client import WebClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.enums import CaseStatus
from dispatch.case.models import CaseCreate, CaseUpdate
from dispatch.entity import service as entity_service
from dispatch.exceptions import ExistsError
from dispatch.incident import flows as incident_flows
from dispatch.participant import service as participant_service
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseEscalateActions,
    CaseNotificationActions,
    CasePaginateActions,
    CaseReportActions,
    CaseResolveActions,
    CaseShortcutCallbacks,
    SignalSnoozeActions,
    SignalNotificationActions,
)
from dispatch.plugins.dispatch_slack.case.messages import create_case_message
from dispatch.plugins.dispatch_slack.config import SlackConversationConfiguration
from dispatch.plugins.dispatch_slack.decorators import message_dispatcher
from dispatch.plugins.dispatch_slack.fields import (
    case_priority_select,
    case_status_select,
    case_type_select,
    DefaultBlockIds,
    description_input,
    entity_select,
    incident_priority_select,
    incident_type_select,
    project_select,
    relative_date_picker_input,
    resolution_input,
    case_resolution_reason_select,
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
from dispatch.plugins.dispatch_slack.models import SubjectMetadata, CaseSubjects, SignalSubjects
from dispatch.plugins.dispatch_slack.service import get_user_email
from dispatch.project import service as project_service
from dispatch.search.utils import create_filter_expression
from dispatch.signal import service as signal_service
from dispatch.signal.models import SignalFilterCreate, SignalFilterRead, SignalUpdate


def configure(config: SlackConversationConfiguration):
    """Maps commands/events to their functions."""
    # don't need an incident context
    app.command(config.slack_command_list_signals, middleware=[db_middleware])(
        handle_list_signals_command
    )


# Commands


def handle_list_signals_command(
    ack: Ack,
    body: dict,
    db_session: Session,
    context: BoltContext,
    client: WebClient,
) -> None:
    ack()

    projects = project_service.get_all(db_session=db_session)
    conversation_name = dispatch_slack_service.get_conversation_name_by_id(
        client, context.channel_id
    )

    signals = []
    for project in projects:
        signals.extend(
            signal_service.get_all_by_conversation_target(
                db_session=db_session, project_id=project.id, conversation_target=conversation_name
            )
        )

    if not signals:
        modal = Modal(
            title="Signal Definition List",
            blocks=[
                Context(elements=[f"There are no signals configured for {conversation_name}"]),
            ],
            close="Close",
        ).build()

        return client.views_open(trigger_id=body["trigger_id"], view=modal)

    limit = 25
    current_page = 0
    total_pages = len(signals) // limit + (1 if len(signals) % limit > 0 else 0)

    _draw_list_signal_modal(
        client=client,
        body=body,
        db_session=db_session,
        conversation_name=conversation_name,
        current_page=current_page,
        total_pages=total_pages,
        first_render=True,
    )


def _draw_list_signal_modal(
    client: WebClient,
    body: dict,
    db_session: Session,
    conversation_name: str,
    current_page: int,
    total_pages: int,
    first_render: bool,
) -> None:
    """Draw the signal definition list modal.

    Args:
        client (WebClient): A Slack WebClient object that provides a convenient interface to the Slack API.
        body (dict): A dictionary that contains the original request payload from Slack.
        db_session (Session): A SQLAlchemy database session.
        conversation_name (str): The name of the Slack conversation.
        current_page (int): The current page number.
        total_pages (int): The total number of pages.
        first_render (bool): A boolean indicating whether the modal is being rendered for the first time.

    Returns:
        None

    Raises:
        None

    Example:
        client = WebClient(token=<SLACK_APP_TOKEN>)
        body = {
            "trigger_id": "836215173894.4768581721.6f8ab1fcee0478f0e6c0c2b0dc9f0c7a",
        }
        db_session = Session()
        conversation_name = "test_conversation"
        current_page = 0
        total_pages = 3
        first_render = True
        _draw_list_signal_modal(
            client, body, db_session, conversation_name, current_page, total_pages, first_render
        )
    """
    modal = Modal(
        title="Signal Definition List",
        blocks=_build_signal_list_modal_blocks(
            db_session=db_session,
            conversation_name=conversation_name,
            current_page=current_page,
            total_pages=total_pages,
        ),
        close="Close",
        private_metadata=json.dumps(
            {
                "conversation_name": conversation_name,
                "current_page": current_page,
                "total_pages": total_pages,
            }
        ),
    ).build()

    client.views_open(
        trigger_id=body["trigger_id"], view=modal
    ) if first_render is True else client.views_update(view_id=body["view"]["id"], view=modal)


def _build_signal_list_modal_blocks(
    db_session: Session,
    conversation_name: str,
    current_page: int,
    total_pages: int,
) -> list:
    """Builds a list of blocks for a modal view displaying signals.

    This function creates a list of blocks that represent signals that are filtered by conversation_name. The list of signals
    is paginated and limited to 25 signals per page.

    The function returns the blocks with pagination controls that display the current page and allows navigation to the previous
    and next pages.

    Args:
        db_session (Session): The database session.
        conversation_name (str): The name of the conversation to filter signals by.
        current_page (int): The current page being displayed.
        total_pages (int): The total number of pages.

    Returns:
        list: A list of blocks representing the signals and pagination controls.

    Example:
        >>> blocks = _build_signal_list_modal_blocks(db_session, "conversation_name", 1, 2)
        >>> len(blocks)
            26
    """

    blocks = []
    limit = 25
    start_index = current_page * limit
    end_index = start_index + limit - 1

    projects = project_service.get_all(db_session=db_session)
    signals = []
    for project in projects:
        signals.extend(
            signal_service.get_all_by_conversation_target(
                db_session=db_session, project_id=project.id, conversation_target=conversation_name
            )
        )

    limited_signals = []
    for idx, signal in enumerate(signals[start_index : end_index + 1], start_index + 1):  # noqa
        limited_signals.append(signal)

        button_metadata = SubjectMetadata(
            type=SignalSubjects.signal,
            organization_slug=signal.project.organization.slug,
            id=signal.id,
            project_id=signal.project.id,
        ).json()

        blocks.extend(
            [
                Section(
                    text=signal.name,
                    accessory=Button(
                        text="Snooze",
                        value=button_metadata,
                        action_id=SignalNotificationActions.snooze,
                    ),
                ),
                Context(
                    elements=[MarkdownText(text=f"{signal.variant}" if signal.variant else "N/A")]
                ),
            ]
        )
        # Don't add a divider if we are at the last signal
        if idx != len(signals[start_index : end_index + 1]):  # noqa
            blocks.extend([Divider()])

    pagination_blocks = [
        Actions(
            block_id="pagination",
            elements=[
                Button(
                    text="Previous",
                    action_id=CasePaginateActions.list_signal_previous,
                    style="danger" if current_page == 0 else "primary",
                ),
                Button(
                    text="Next",
                    action_id=CasePaginateActions.list_signal_next,
                    style="danger" if current_page == total_pages - 1 else "primary",
                ),
            ],
        )
    ]

    return blocks + pagination_blocks if len(signals) > limit else blocks


@app.action(
    CasePaginateActions.list_signal_next, middleware=[action_context_middleware, db_middleware]
)
def handle_next_action(ack: Ack, body: dict, client: WebClient, db_session: Session):
    """Handle the 'next' action in the signal list modal.

    This function is called when the user clicks the 'next' button in the signal list modal. It increments the current page
    of the modal and updates the view with the new page.

    Args:
        ack (function): The function to acknowledge the action request.
        db_session (Session): The database session to query for signal data.
        body (dict): The request payload from the action.
        client (WebClient): The Slack API WebClient to interact with the Slack API.
    """
    ack()

    metadata = json.loads(body["view"]["private_metadata"])

    current_page = metadata["current_page"]
    total_pages = metadata["total_pages"]
    conversation_name = metadata["conversation_name"]

    if current_page < total_pages - 1:
        current_page += 1

    _draw_list_signal_modal(
        client=client,
        body=body,
        db_session=db_session,
        conversation_name=conversation_name,
        current_page=current_page,
        total_pages=total_pages,
        first_render=False,
    )


@app.action(
    CasePaginateActions.list_signal_previous, middleware=[action_context_middleware, db_middleware]
)
def handle_previous_action(ack: Ack, body: dict, client: WebClient, db_session: Session):
    """Handle the 'previous' action in the signal list modal.

    This function is called when the user clicks the 'previous' button in the signal list modal. It decrements the current page
    of the modal and updates the view with the new page.

    Args:
        ack (function): The function to acknowledge the action request.
        db_session (Session): The database session to query for signal data.
        body (dict): The request payload from the action.
        client (WebClient): The Slack API WebClient to interact with the Slack API.
    """
    ack()

    metadata = json.loads(body["view"]["private_metadata"])

    current_page = metadata["current_page"]
    total_pages = metadata["total_pages"]
    conversation_name = metadata["conversation_name"]

    if current_page > 0:
        current_page -= 1

    _draw_list_signal_modal(
        client=client,
        body=body,
        db_session=db_session,
        conversation_name=conversation_name,
        current_page=current_page,
        total_pages=total_pages,
        first_render=False,
    )


@app.action(SignalNotificationActions.snooze, middleware=[button_context_middleware, db_middleware])
def snooze_button_click(
    ack: Ack, body: dict, client: WebClient, context: BoltContext, db_session: Session
) -> None:
    ack()

    subject = context["subject"]

    if subject.type == SignalSubjects.signal_instance:
        instance = signal_service.get_signal_instance(
            db_session=db_session, signal_instance_id=subject.id
        )
        signal = signal_service.get(db_session=db_session, signal_id=instance.signal.id)
        subject.id = signal.id

    blocks = [
        title_input(placeholder="A name for your snooze filter."),
        description_input(placeholder="Provide a description for your snooze filter."),
        entity_select(db_session=db_session, project_id=subject.project_id),
        Context(
            elements=[
                MarkdownText(
                    text="Signal's that contain all selected entities will be snoozed for the configured timeframe."
                )
            ]
        ),
        relative_date_picker_input(label="Expiration"),
    ]

    modal = Modal(
        title="Snooze Signal",
        blocks=blocks,
        submit="Preview",
        close="Close",
        callback_id=SignalSnoozeActions.preview,
        private_metadata=context["subject"].json(),
    ).build()

    # We are not in a modal
    if trigger_id := body.get("trigger_id"):
        client.views_open(trigger_id=trigger_id, view=modal)
    else:
        # We are inside of a modal
        client.views_update(view_id=body["view"]["id"], view=modal)


@app.view(
    SignalSnoozeActions.preview,
    middleware=[
        action_context_middleware,
        db_middleware,
        modal_submit_middleware,
    ],
)
def handle_snooze_preview_event(
    ack: Ack,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
) -> None:
    if form_data.get(DefaultBlockIds.title_input):
        title = form_data[DefaultBlockIds.title_input]

    name_taken = signal_service.get_signal_filter_by_name(
        db_session=db_session, project_id=context["subject"].project_id, name=title
    )
    if name_taken:
        modal = Modal(
            title="Name Taken",
            close="Close",
            blocks=[
                Context(
                    elements=[
                        MarkdownText(
                            text=f"A signal filter with the name '{title}' already exists."
                        )
                    ]
                )
            ],
        ).build()
        return ack(response_action="update", view=modal)

    if form_data.get(DefaultBlockIds.entity_select):
        entity_ids = [entity["value"] for entity in form_data[DefaultBlockIds.entity_select]]

    preview_signal_instances = entity_service.get_signal_instances_with_entities(
        db_session=db_session, signal_id=context["subject"].id, entity_ids=entity_ids, days_back=90
    )

    text = (
        "Examples matching your filter:"
        if preview_signal_instances
        else "No signals matching your filter."
    )

    blocks = [Context(elements=[MarkdownText(text=text)])]

    if preview_signal_instances:
        # Only show 5 examples
        for signal_instance in preview_signal_instances[:5]:
            blocks.extend(
                [
                    Section(text=signal_instance.signal.name),
                    Context(
                        elements=[
                            MarkdownText(
                                text=f" Case: {signal_instance.case.name if signal_instance.case else 'N/A'}"
                            )
                        ]
                    ),
                    Context(
                        elements=[
                            MarkdownText(
                                text=f" Created: {signal_instance.case.created_at if signal_instance.case else 'N/A'}"
                            )
                        ]
                    ),
                ]
            )

    modal = Modal(
        title="Add Snooze",
        submit="Create",
        close="Close",
        blocks=blocks,
        callback_id=SignalSnoozeActions.submit,
        private_metadata=json.dumps({"form_data": form_data, "subject": context["subject"].json()}),
    ).build()
    ack(response_action="update", view=modal)


def ack_snooze_submission_event(ack: Ack, mfa_enabled: bool) -> None:
    """Handles the add snooze submission event acknowledgement."""
    text = (
        "Adding snooze submission event..."
        if mfa_enabled is False
        else "Sending MFA push notification, please confirm to create Snooze filter..."
    )
    modal = Modal(
        title="Add Snooze",
        close="Close",
        blocks=[Section(text=text)],
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    SignalSnoozeActions.submit,
    middleware=[
        action_context_middleware,
        db_middleware,
        user_middleware,
        modal_submit_middleware,
    ],
)
def handle_snooze_submission_event(
    ack: Ack,
    body,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
) -> None:
    """Handle the submission event of the snooze modal.

    This function is executed when a user submits the snooze modal. It first
    sends an MFA push notification to the user to confirm the action. If the
    user accepts the MFA prompt, the function retrieves the relevant information
    from the form data and creates a new signal filter. The new filter is then
    added to the existing filters for the signal. Finally, the function updates
    the modal view to show the result of the operation.

    Args:
        ack (Ack): The acknowledgement function.
        body (dict): The request body.
        client (WebClient): The Slack API client.
        context (BoltContext): The context data.
        db_session (Session): The database session.
        form_data (dict): The form data submitted by the user.
        user (DispatchUser): The Dispatch user who submitted the form.
    """
    metadata = json.loads(body["view"]["private_metadata"])
    subject = json.loads(metadata["subject"])

    mfa_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=subject["project_id"], plugin_type="auth-mfa"
    )
    mfa_enabled = True if mfa_plugin else False

    ack_snooze_submission_event(ack=ack, mfa_enabled=mfa_enabled)

    def _create_snooze_filter(
        db_session: Session,
        form_data: dict,
        subject: dict,
        user: DispatchUser,
    ) -> None:
        # Get the existing filters for the signal
        signal = signal_service.get(db_session=db_session, signal_id=subject["id"])

        # Create the new filter from the form data
        if form_data.get(DefaultBlockIds.entity_select):
            entities = [
                {"name": entity["name"], "value": entity["value"]}
                for entity in form_data[DefaultBlockIds.entity_select]
            ]

        if form_data.get(DefaultBlockIds.description_input):
            description = form_data[DefaultBlockIds.description_input]

        if form_data.get(DefaultBlockIds.title_input):
            name = form_data[DefaultBlockIds.title_input]

        if form_data.get(DefaultBlockIds.relative_date_picker_input):
            delta: str = form_data[DefaultBlockIds.relative_date_picker_input]["value"]
            delta = timedelta(
                hours=int(delta.split(":")[0]),
                minutes=int(delta.split(":")[1]),
                seconds=int(delta.split(":")[2]),
            )
            date = datetime.now() + delta

        project = project_service.get(db_session=db_session, project_id=subject["project_id"])
        filters = {
            "entity": entities,
        }

        expression = create_filter_expression(filters, "Entity")

        # Create a new filter with the selected entities and entity types
        filter_in = SignalFilterCreate(
            name=name,
            description=description,
            expiration=date,
            expression=expression,
            project=project,
        )
        try:
            new_filter = signal_service.create_signal_filter(
                db_session=db_session, creator=user, signal_filter_in=filter_in
            )
        except IntegrityError:
            raise ExistsError("A signal filter with this name already exists.") from None

        signal_in = SignalUpdate(
            id=signal.id,
            name=signal.name,
            owner=signal.owner,
            external_id=signal.external_id,
            project=project,
            filters=[SignalFilterRead.from_orm(new_filter)],
        )

        signal = signal_service.update(db_session=db_session, signal=signal, signal_in=signal_in)

    if mfa_enabled is False:
        _create_snooze_filter(
            db_session=db_session,
            form_data=metadata["form_data"],
            user=user,
            subject=subject,
        )

        modal = Modal(
            title="Add Snooze",
            close="Close",
            blocks=[Section(text="Adding Snooze... Success!")],
        ).build()

        client.views_update(
            view_id=body["view"]["id"],
            view=modal,
        )

    if mfa_enabled is True:
        # Send the MFA push notification
        email = context["user"].email
        username, _ = email.split("@")
        # In Duo it seems the username here can either be an email or regular username
        # depending on how your Duo instance is setup. We try to manage both cases here.
        try:
            response = mfa_plugin.instance.send_push_notification(
                username=username, type="Are you creating a signal filter in Dispatch?"
            )
        except RuntimeError as e:
            if "Invalid request parameters (username)" in str(e):
                response = mfa_plugin.instance.send_push_notification(
                    username=email, type="Are you creating a signal filter in Dispatch?"
                )
            else:
                raise e from None

        if response.get("result") == "allow":
            # Get the existing filters for the signal
            _create_snooze_filter(
                db_session=db_session,
                form_data=metadata["form_data"],
                user=user,
                subject=subject,
            )

            modal = Modal(
                title="Add Snooze",
                close="Close",
                blocks=[Section(text="Adding Snooze... Success!")],
            ).build()

            client.views_update(
                view_id=body["view"]["id"],
                view=modal,
            )
        else:
            text = (
                "Adding Snooze failed, the MFA request timed out."
                if response.get("status") == "timeout"
                else "Adding Snooze failed, you must accept the MFA prompt."
            )
            modal = Modal(
                title="Add Snooze",
                close="Close",
                blocks=[Section(text=text)],
            ).build()

            client.views_update(
                view_id=body["view"]["id"],
                view=modal,
            )


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
    subject=CaseSubjects.case, exclude={"subtype": ["channel_join", "channel_leave"]}
)  # we ignore channel join and leave messages
def handle_new_participant_message(
    ack: Ack, user: DispatchUser, context: BoltContext, db_session: Session, client: WebClient
) -> None:
    """Looks for new participants that have starting chatting for the first time."""
    ack()
    participant = case_flows.case_add_or_reactive_participant_flow(
        case_id=context["subject"].id,
        user_email=user.email,
        db_session=db_session,
        add_to_conversation=False,
    )
    participant.user_conversation_id = context["user_id"]


@message_dispatcher.add(
    subject=CaseSubjects.case, exclude={"subtype": ["channel_join", "channel_leave"]}
)  # we ignore channel join and leave messages
def handle_new_participant_added(
    ack: Ack, payload: dict, context: BoltContext, db_session: Session, client: WebClient
) -> None:
    """Looks for new participants being added to conversation via @<user-name>"""
    ack()
    participants = re.findall(r"\<\@([a-zA-Z0-9]*)\>", payload["text"])
    for user_id in participants:
        user_email = get_user_email(client=client, user_id=user_id)

        participant = case_flows.case_add_or_reactive_participant_flow(
            case_id=context["subject"].id,
            user_email=user_email,
            db_session=db_session,
            add_to_conversation=False,
        )
        participant.user_conversation_id = user_id


@message_dispatcher.add(
    subject=CaseSubjects.case, exclude={"subtype": ["channel_join", "channel_leave"]}
)  # we ignore channel join and leave messages
def handle_case_participant_role_activity(
    ack: Ack, db_session: Session, context: BoltContext, user: DispatchUser
) -> None:
    ack()

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
    subject=CaseSubjects.case, exclude={"subtype": ["channel_join", "group_join"]}
)  # we ignore user channel and group join messages
def handle_case_after_hours_message(
    ack: Ack,
    context: BoltContext,
    client: WebClient,
    db_session: Session,
    respond: Respond,
    payload: dict,
    user: DispatchUser,
) -> None:
    """Notifies the user that this case is currently in after hours mode."""
    ack()

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
                thread_ts=payload["thread_ts"],
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
        case_resolution_reason_select(),
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
        resolution_reason=form_data[DefaultBlockIds.case_resolution_reason_select],
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


@app.action(SignalNotificationActions.view, middleware=[button_context_middleware, db_middleware])
def signal_button_click(
    ack: Ack, body: dict, db_session: Session, context: BoltContext, client: WebClient
):
    ack()
    signal = signal_service.get_signal_instance(
        db_session=db_session, signal_instance_id=context["subject"].id
    )

    blocks = [Section(text=f"```{json.dumps(signal.raw, indent=2)}```")]

    modal = Modal(
        title="Raw Signal",
        blocks=blocks,
        close="Close",
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)
