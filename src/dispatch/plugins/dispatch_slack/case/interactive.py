import json
import logging
from datetime import datetime, timedelta, timezone
from functools import partial
from uuid import UUID

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
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser, MfaChallengeStatus
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.case.enums import CaseResolutionReason, CaseStatus
from dispatch.case.models import Case, CaseCreate, CaseRead, CaseUpdate
from dispatch.case.type import service as case_type_service
from dispatch.conversation import flows as conversation_flows
from dispatch.entity import service as entity_service
from dispatch.enums import EventType, SubjectNames, UserRoles, Visibility
from dispatch.event import service as event_service
from dispatch.exceptions import ExistsError
from dispatch.individual.models import IndividualContactRead
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantUpdate
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseEditActions,
    CaseEscalateActions,
    CaseMigrateActions,
    CaseNotificationActions,
    CasePaginateActions,
    CaseReportActions,
    CaseResolveActions,
    CaseShortcutCallbacks,
    SignalEngagementActions,
    SignalNotificationActions,
    SignalSnoozeActions,
)
from dispatch.plugins.dispatch_slack.case.messages import (
    create_case_message,
    create_signal_engagement_message,
    create_manual_engagement_message,
)
from dispatch.plugins.dispatch_slack.config import SlackConversationConfiguration
from dispatch.plugins.dispatch_slack.decorators import message_dispatcher
from dispatch.plugins.dispatch_slack.enums import SlackAPIErrorCode
from dispatch.plugins.dispatch_slack.fields import (
    DefaultBlockIds,
    case_priority_select,
    case_resolution_reason_select,
    case_status_select,
    case_type_select,
    description_input,
    entity_select,
    incident_priority_select,
    incident_type_select,
    project_select,
    relative_date_picker_input,
    resolution_input,
    title_input,
    participant_select,
)
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    button_context_middleware,
    command_context_middleware,
    configuration_middleware,
    db_middleware,
    engagement_button_context_middleware,
    modal_submit_middleware,
    shortcut_context_middleware,
    subject_middleware,
    user_middleware,
)
from dispatch.plugins.dispatch_slack.modals.common import send_success_modal
from dispatch.plugins.dispatch_slack.models import (
    CaseSubjects,
    FormData,
    FormMetadata,
    SignalSubjects,
    SubjectMetadata,
)
from dispatch.project import service as project_service
from dispatch.search.utils import create_filter_expression
from dispatch.service import flows as service_flows
from dispatch.signal import service as signal_service
from dispatch.signal.enums import SignalEngagementStatus
from dispatch.signal.models import (
    Signal,
    SignalEngagement,
    SignalFilter,
    SignalFilterCreate,
    SignalInstance,
)
from dispatch.ticket import flows as ticket_flows

log = logging.getLogger(__name__)


def configure(config: SlackConversationConfiguration):
    """Maps commands/events to their functions."""
    case_command_context_middleware = partial(
        command_context_middleware,
        expected_subject=SubjectNames.CASE,
    )

    # don't need an incident context
    app.command(config.slack_command_list_signals, middleware=[db_middleware])(
        handle_list_signals_command
    )

    middleware = [
        subject_middleware,
        configuration_middleware,
        case_command_context_middleware,
    ]

    app.command(config.slack_command_create_case, middleware=[db_middleware])(report_issue)

    app.command(config.slack_command_escalate_case, middleware=middleware)(
        handle_escalate_case_command
    )

    # non-sensitive commands
    middleware = [
        subject_middleware,
        configuration_middleware,
        case_command_context_middleware,
        user_middleware,
    ]

    app.command(config.slack_command_update_case, middleware=middleware)(handle_update_case_command)

    app.command(config.slack_command_engage_user, middleware=middleware)(handle_engage_user_command)


# Commands


def handle_escalate_case_command(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    """Handles list participants command."""
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    already_escalated = True if case.escalated_at else False
    if already_escalated:
        modal = Modal(
            title="Already Escalated",
            blocks=[Section(text="This case has already been escalated to an incident.")],
            close="Close",
        ).build()

        return client.views_open(
            trigger_id=body["trigger_id"],
            view=modal,
        )

    default_title = case.name
    default_description = case.description
    default_project = {"text": case.project.name, "value": case.project.id}

    blocks = [
        Context(elements=[MarkdownText(text="Accept the defaults or adjust as needed.")]),
        title_input(initial_value=default_title),
        description_input(initial_value=default_description),
        project_select(
            db_session=db_session,
            initial_option=default_project,
            action_id=CaseEscalateActions.project_select,
            dispatch_action=True,
        ),
        incident_type_select(
            db_session=db_session,
            initial_option=None,
            project_id=case.project.id,
            block_id=DefaultBlockIds.incident_type_select,
        ),
        incident_priority_select(
            db_session=db_session,
            project_id=case.project.id,
            initial_option=None,
            optional=True,
            block_id=DefaultBlockIds.incident_priority_select,
        ),
    ]

    modal = Modal(
        title="Escalate Case",
        submit="Escalate",
        blocks=blocks,
        close="Close",
        callback_id=CaseEscalateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(
        trigger_id=body["trigger_id"],
        view=modal,
    )


def handle_update_case_command(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    ack()

    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    try:
        user_lookup_response = client.users_lookupByEmail(email=case.assignee.individual.email)
        assignee_initial_user = user_lookup_response["user"]["id"]
    except SlackApiError as e:
        if e.response["error"] == SlackAPIErrorCode.USERS_NOT_FOUND:
            log.warning(
                f"Unable to fetch default assignee for {case.assignee.individual.email}: {e}"
            )
        assignee_initial_user = None

    statuses = [{"text": str(s), "value": str(s)} for s in CaseStatus if s != CaseStatus.escalated]

    blocks = [
        title_input(initial_value=case.title),
        description_input(initial_value=case.description),
        case_resolution_reason_select(optional=True),
        resolution_input(initial_value=case.resolution),
        assignee_select(initial_user=assignee_initial_user),
        case_status_select(
            initial_option={"text": case.status, "value": case.status}, statuses=statuses
        ),
        Context(
            elements=[
                MarkdownText(
                    text=f"Note: Cases cannot be escalated here. Please use the `{context['config'].slack_command_escalate_case}` slash command."
                )
            ]
        ),
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
        callback_id=CaseEditActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_engage_oncall_submission_event(ack: Ack) -> None:
    """Handles engage oncall acknowledgment."""
    modal = Modal(
        title="Escalate Case",
        close="Close",
        blocks=[Section(text="Escalating case to an incident...")],
    ).build()
    ack(response_action="update", view=modal)


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


def handle_engage_user_command(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
) -> None:
    """Handles engage user command."""
    ack()

    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    default_engagement = "We'd like to verify your identity. Can you please confirm this is you?"

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="Accept the defaults or adjust as needed. Person to engage must already be a participant in the case."
                )
            ]
        ),
        participant_select(label="Person to engage", participants=case.participants),
        description_input(label="Engagement text", initial_value=default_engagement),
    ]

    modal = Modal(
        title="Engage user via MFA",
        submit="Engage",
        blocks=blocks,
        close="Close",
        callback_id="manual-engage-mfa",
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(
        trigger_id=body["trigger_id"],
        view=modal,
    )


@app.view(
    "manual-engage-mfa",
    middleware=[
        action_context_middleware,
        db_middleware,
        modal_submit_middleware,
    ],
)
def engage(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
) -> None:
    """Handles the engage user action."""
    ack()

    if form_data.get(DefaultBlockIds.participant_select):
        participant_id = form_data[DefaultBlockIds.participant_select]["value"]
        participant = participant_service.get(db_session=db_session, participant_id=participant_id)
        if participant:
            user_email = participant.individual.email
        else:
            log.error(f"Participant not found for id {participant_id} when trying to engage user")
            return
    else:
        return

    if form_data.get(DefaultBlockIds.description_input):
        engagement = form_data[DefaultBlockIds.description_input]
    else:
        log.warning("Engagement text not found")
        return

    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    user = client.users_lookupByEmail(email=user_email)

    result = client.chat_postMessage(
        text="Engaging user...",
        channel=case.conversation.channel_id,
        thread_ts=case.conversation.thread_id if case.has_thread else None,
    )
    thread_ts = result.data.get("ts")

    blocks = create_manual_engagement_message(
        case=case,
        channel_id=case.conversation.channel_id,
        engagement=engagement,
        user_email=user_email,
        user_id=user["user"]["id"],
        thread_ts=thread_ts,
    )
    client.chat_update(
        blocks=blocks,
        channel=case.conversation.channel_id,
        ts=thread_ts,
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

    (
        client.views_open(trigger_id=body["trigger_id"], view=modal)
        if first_render is True
        else client.views_update(view_id=body["view"]["id"], view=modal)
    )


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
    """Handles the snooze button click event."""
    ack()

    subject = context["subject"]

    if subject.type == SignalSubjects.signal_instance:
        instance = signal_service.get_signal_instance(
            db_session=db_session, signal_instance_id=subject.id
        )
        subject.id = instance.signal.id

    signal = signal_service.get(db_session=db_session, signal_id=subject.id)
    blocks = [
        Context(elements=[MarkdownText(text=f"{signal.name}")]),
        Divider(),
        title_input(placeholder="A name for your snooze filter."),
        description_input(placeholder="Provide a description for your snooze filter."),
        relative_date_picker_input(label="Expiration"),
    ]

    # not all signals will have entities and slack doesn't like empty selects
    entity_select_block = entity_select(
        db_session=db_session,
        signal_id=signal.id,
        optional=True,
    )

    if entity_select_block:
        blocks.append(entity_select_block)
        blocks.append(
            Context(
                elements=[
                    MarkdownText(
                        text="Signals that contain all selected entities will be snoozed for the configured timeframe."
                    )
                ]
            )
        )

    modal = Modal(
        title="Snooze Signal",
        blocks=blocks,
        submit="Preview",
        close="Close",
        callback_id=SignalSnoozeActions.preview,
        private_metadata=context["subject"].json(),
    ).build()

    if view_id := body.get("view", {}).get("id"):
        client.views_update(view_id=view_id, view=modal)
    else:
        client.views_open(trigger_id=body["trigger_id"], view=modal)


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
    """Handles the snooze preview event."""
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
            db_session=db_session,
            signal_id=context["subject"].id,
            entity_ids=entity_ids,
            days_back=90,
        )

        text = (
            "Examples matching your filter:"
            if preview_signal_instances
            else "No signals matching your filter."
        )
    else:
        preview_signal_instances = None
        text = "No entities selected. All instances of this signal will be snoozed."

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

    private_metadata = FormMetadata(
        form_data=form_data,
        **context["subject"].dict(),
    ).json()
    modal = Modal(
        title="Add Snooze",
        submit="Create",
        close="Close",
        blocks=blocks,
        callback_id=SignalSnoozeActions.submit,
        private_metadata=private_metadata,
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    SignalSnoozeActions.submit,
    middleware=[
        action_context_middleware,
        db_middleware,
        user_middleware,
    ],
)
def handle_snooze_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
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
        user (DispatchUser): The Dispatch user who submitted the form.
    """
    mfa_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=context["subject"].project_id, plugin_type="auth-mfa"
    )
    mfa_enabled = True if mfa_plugin else False

    def _create_snooze_filter(
        db_session: Session,
        subject: SubjectMetadata,
        user: DispatchUser,
    ) -> None:
        form_data: FormData = subject.form_data
        # Get the existing filters for the signal
        signal = signal_service.get(db_session=db_session, signal_id=subject.id)
        # Create the new filter from the form data
        if form_data.get(DefaultBlockIds.entity_select):
            entities = [
                {"id": int(entity.value)} for entity in form_data[DefaultBlockIds.entity_select]
            ]
        else:
            entities = []

        description = form_data[DefaultBlockIds.description_input]
        name = form_data[DefaultBlockIds.title_input]
        delta: str = form_data[DefaultBlockIds.relative_date_picker_input].value
        # Check if the 'delta' string contains days
        # Example: '1 day, 0:00:00' contains days, while '0:01:00' does not
        if ", " in delta:
            # Split the 'delta' string into days and time parts
            # Example: '1 day, 0:00:00' -> days: '1 day' and time_str: '0:00:00'
            days, time_str = delta.split(", ")

            # Extract the integer value of days from the days string
            # Example: '1 day' -> 1
            days = int(days.split(" ")[0])
        else:
            # If the 'delta' string does not contain days, set days to 0
            days = 0

            # Directly assign the 'delta' string to the time_str variable
            time_str = delta

        # Split the 'time_str' variable into hours, minutes, and seconds
        # Convert each part to an integer
        # Example: '0:01:00' -> hours: 0, minutes: 1, seconds: 0
        hours, minutes, seconds = [int(x) for x in time_str.split(":")]

        # Create a timedelta object using the extracted days, hours, minutes, and seconds
        delta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )

        # Calculate the new date by adding the timedelta object to the current date and time
        date = datetime.now(tz=timezone.utc) + delta

        project = project_service.get(db_session=db_session, project_id=signal.project_id)

        # None expression is for cases when no entities are selected, in which case
        # the filter will apply to all instances of the signal
        if entities:
            filters = {
                "entity": entities,
            }
            expression = create_filter_expression(filters, "Entity")
        else:
            expression = []

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

        signal.filters.append(new_filter)
        db_session.commit()
        return new_filter

    channel_id = context["subject"].channel_id
    thread_id = context["subject"].thread_id

    # Check if last_mfa_time was within the last hour
    if not mfa_enabled:
        new_filter = _create_snooze_filter(
            db_session=db_session,
            user=user,
            subject=context["subject"],
        )
        signal = signal_service.get(db_session=db_session, signal_id=context["subject"].id)
        post_snooze_message(
            db_session=db_session,
            client=client,
            channel=channel_id,
            user=user,
            signal=signal,
            new_filter=new_filter,
            thread_ts=thread_id,
        )
        send_success_modal(
            client=client,
            view_id=body["view"]["id"],
            title="Add Snooze",
            message="Snooze Filter added successfully.",
        )
    else:
        challenge, challenge_url = mfa_plugin.instance.create_mfa_challenge(
            action="signal-snooze",
            current_user=user,
            db_session=db_session,
            project_id=context["subject"].project_id,
        )
        ack_mfa_required_submission_event(
            ack=ack, mfa_enabled=mfa_enabled, challenge_url=challenge_url
        )

        # wait for the mfa challenge
        response = mfa_plugin.instance.wait_for_challenge(
            challenge_id=challenge.challenge_id,
            db_session=db_session,
        )

        if response == MfaChallengeStatus.APPROVED:
            new_filter = _create_snooze_filter(
                db_session=db_session,
                user=user,
                subject=context["subject"],
            )
            signal = signal_service.get(db_session=db_session, signal_id=context["subject"].id)
            post_snooze_message(
                db_session=db_session,
                client=client,
                channel=channel_id,
                user=user,
                signal=signal,
                new_filter=new_filter,
                thread_ts=thread_id,
            )
            send_success_modal(
                client=client,
                view_id=body["view"]["id"],
                title="Add Snooze",
                message="Snooze Filter added successfully.",
            )
            user.last_mfa_time = datetime.now()
            db_session.commit()
        else:
            if response == MfaChallengeStatus.EXPIRED:
                text = "Adding Snooze failed, the MFA request timed out."
            elif response == MfaChallengeStatus.DENIED:
                text = "Adding Snooze failed, challenge did not complete succsfully."
            else:
                text = "Adding Snooze failed, you must accept the MFA prompt."

            modal = Modal(
                title="Add Snooze",
                close="Close",
                blocks=[Section(text=text)],
            ).build()

            client.views_update(
                view_id=body["view"]["id"],
                view=modal,
            )


def post_snooze_message(
    client: WebClient,
    channel: str,
    user: DispatchUser,
    signal: Signal,
    db_session: Session,
    new_filter: SignalFilter,
    thread_ts: str | None = None,
):
    def extract_entity_ids(expression: list[dict]) -> list[int]:
        entity_ids = []
        for item in expression:
            if isinstance(item, dict) and "or" in item:
                for condition in item["or"]:
                    if condition.get("model") == "Entity" and condition.get("field") == "id":
                        entity_ids.append(int(condition.get("value")))
        return entity_ids

    entity_ids = extract_entity_ids(new_filter.expression)

    if entity_ids:
        entities = []
        for entity_id in entity_ids:
            entity = entity_service.get(db_session=db_session, entity_id=entity_id)
            if entity:
                entities.append(entity)
        entities_text = ", ".join([f"{entity.value} ({entity.id})" for entity in entities])
    else:
        entities_text = "All"

    message = (
        f":zzz: *New Signal Snooze Added*\n"
        f"• User: {user.email}\n"
        f"• Signal: {signal.name}\n"
        f"• Snooze Name: {new_filter.name}\n"
        f"• Description: {new_filter.description}\n"
        f"• Expiration: {new_filter.expiration}\n"
        f"• Entities: {entities_text}"
    )
    client.chat_postMessage(channel=channel, text=message, thread_ts=thread_ts)


def assignee_select(
    placeholder: str = "Select Assignee",
    initial_user: str = None,
    action_id: str = None,
    block_id: str = DefaultBlockIds.case_assignee_select,
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
    participant = case_flows.case_add_or_reactivate_participant_flow(
        case_id=context["subject"].id,
        user_email=user.email,
        db_session=db_session,
        add_to_conversation=False,
    )
    participant.user_conversation_id = context["user_id"]

    for participant_role in participant.active_roles:
        participant_role.activity += 1

        # re-assign role once threshold is reached
        if participant_role.role == ParticipantRoleType.observer:
            if participant_role.activity >= 3:  # three messages sent to the case channel
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
                event_service.log_case_event(
                    db_session=db_session,
                    source="Slack Plugin - Conversation Management",
                    description=(
                        f"{participant.individual.name}'s role changed from {participant_role.role} to "
                        f"{ParticipantRoleType.participant} due to activity in the case channel"
                    ),
                    case_id=context["subject"].id,
                    type=EventType.participant_updated,
                )

        db_session.commit()


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
            case_id=context["subject"].id, user_email=user.email, db_session=db_session
        )
        participant.user_conversation_id = context["user_id"]

    # if a participant is active mark the case as being in the triaged state
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    if case.status == CaseStatus.new:
        case_flows.case_status_transition_flow_dispatcher(
            case=case,
            current_status=CaseStatus.triage,
            db_session=db_session,
            previous_status=case.status,
            organization_slug=context["subject"].organization_slug,
        )
        case.status = CaseStatus.triage

        # we update the ticket
        ticket_flows.update_case_ticket(case=case, db_session=db_session)

    case_flows.update_conversation(case, db_session)
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

    # Check if the message is in a thread
    # We should not attempt to raise this message when a message is sent to the main channel.
    if "thread_ts" not in payload:
        return

    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    owner_email = case.assignee.individual.email
    participant = participant_service.get_by_case_id_and_email(
        db_session=db_session, case_id=context["subject"].id, email=user.email
    )
    # handle no participant found
    if not participant:
        log.warning(
            f"Participant not found for {user.email} in case {case.id}. Skipping after hours notification."
        )
        return

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

    # we update the ticket
    ticket_flows.update_case_ticket(case=case, db_session=db_session)

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
            initial_option=(
                {
                    "text": case.case_type.incident_type.name,
                    "value": case.case_type.incident_type.id,
                }
                if case.case_type.incident_type
                else None
            ),
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


def ack_handle_escalation_submission_event(ack: Ack, case: Case) -> None:
    """Handles the escalation submission event."""

    msg = (
        "The case has been escalated to an incident. This channel will be reused for the incident."
        if case.dedicated_channel
        else "The case has been escalated to an incident. All further triage work will take place in the incident channel."
    )
    modal = Modal(
        title="Escalating Case",
        close="Close",
        blocks=[Section(text=msg)],
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    CaseEscalateActions.submit,
    middleware=[
        action_context_middleware,
        user_middleware,
        db_middleware,
        modal_submit_middleware,
    ],
)
def handle_escalation_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
):
    """Handles the escalation submission event."""

    from dispatch.incident.type.service import get_by_name

    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    ack_handle_escalation_submission_event(ack=ack, case=case)

    case.status = CaseStatus.escalated
    db_session.commit()

    modal = Modal(
        title="Case Escalated",
        close="Close",
        blocks=[Section(text="Running case escalation flows...")],
    ).build()

    result = client.views_update(
        view_id=body["view"]["id"],
        trigger_id=body["trigger_id"],
        view=modal,
    )

    incident_type = None
    if form_data.get(DefaultBlockIds.incident_type_select):
        incident_type = get_by_name(
            db_session=db_session,
            project_id=case.project.id,
            name=form_data[DefaultBlockIds.incident_type_select]["name"],
        )

    incident_priority = None
    if form_data.get(DefaultBlockIds.incident_priority_select):
        incident_priority = get_by_name(
            db_session=db_session,
            project_id=case.project.id,
            name=form_data[DefaultBlockIds.incident_priority_select]["name"],
        )
    incident_description = form_data.get(DefaultBlockIds.description_input, case.description)
    title = form_data.get(DefaultBlockIds.title_input, case.title)
    case_flows.case_escalated_status_flow(
        case=case,
        organization_slug=context["subject"].organization_slug,
        db_session=db_session,
        title=title,
        incident_priority=incident_priority,
        incident_type=incident_type,
        incident_description=incident_description,
    )
    incident = case.incidents[0]

    blocks = create_case_message(case=case, channel_id=context["subject"].channel_id)
    if case.has_thread:
        client.chat_update(
            blocks=blocks,
            ts=case.conversation.thread_id,
            channel=case.conversation.channel_id,
        )
        client.chat_postMessage(
            text=f"This case has been escalated to incident {incident.name}. All further triage work will take place in the incident channel.",
            channel=case.conversation.channel_id,
            thread_ts=case.conversation.thread_id if case.has_thread else None,
        )

    # Add all case participants to the incident
    conversation_flows.add_incident_participants_to_conversation(
        incident=incident,
        participant_emails=case.participant_emails,
        db_session=db_session,
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

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        trigger_id=result["trigger_id"],
        title="Case Escalated",
        message="Case escalated successfully.",
    )


@app.action(
    CaseNotificationActions.migrate,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
def create_channel_button_click(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    form_data: dict,
    db_session: Session,
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    case.dedicated_channel = True
    db_session.commit()

    blocks = [
        Section(text="Migrate the thread conversation to a dedicated channel?"),
        Context(elements=[MarkdownText(text="This action will remove the case from this thread.")]),
    ]

    modal = Modal(
        title="Create Case Channel",
        blocks=blocks,
        submit="Create Channel",
        close="Close",
        callback_id=CaseMigrateActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.action(
    CaseNotificationActions.user_mfa,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
def user_mfa_button_click(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
):
    return handle_engage_user_command(
        ack=ack,
        body=body,
        client=client,
        context=context,
        db_session=db_session,
    )


def ack_handle_create_channel_event(ack: Ack, case: Case) -> None:
    """Handles the case channel creation event."""
    msg = (
        "The case already has a dedicated channel. No actions will be performed."
        if case.has_channel
        else "Creating a dedicated case channel..."
    )

    modal = Modal(
        title="Creating Case Channel",
        close="Close",
        blocks=[Section(text=msg)],
    ).build()

    ack(response_action="update", view=modal)


@app.view(
    CaseMigrateActions.submit,
    middleware=[
        action_context_middleware,
        db_middleware,
    ],
)
def handle_create_channel_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
):
    """Handles the escalation submission event."""
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    ack_handle_create_channel_event(ack=ack, case=case)

    case.dedicated_channel = True
    db_session.commit()

    msg = (
        "Creating a dedicated case channel..."
        if not case.has_channel
        else "The case already has a dedicated channel. No actions will be performed."
    )

    modal = Modal(
        title="Creating Case Channel",
        close="Close",
        blocks=[Section(text=msg)],
    ).build()

    result = client.views_update(
        view_id=body["view"]["id"],
        trigger_id=body["trigger_id"],
        view=modal,
    )

    channel_id = case.conversation.channel_id
    thread_id = case.conversation.thread_id

    # Add all case participants to the case channel
    case_flows.case_create_conversation_flow(
        db_session=db_session,
        case=case,
        participant_emails=case.participant_emails,
        conversation_target=None,
    )

    # This should update the original message?
    blocks = create_case_message(case=case, channel_id=channel_id)
    client.chat_update(blocks=blocks, ts=thread_id, channel=channel_id)

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        trigger_id=result["trigger_id"],
        title="Channel Created",
        message="Case channel created successfully.",
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

    # we add the user to the incident conversation
    conversation_flows.add_incident_participants_to_conversation(
        # TODO: handle case where there are multiple related incidents
        incident=case.incidents[0],
        participant_emails=[user.email],
        db_session=db_session,
    )


@app.action(
    CaseNotificationActions.invite_user_case,
    middleware=[button_context_middleware, db_middleware, user_middleware],
)
def handle_case_notification_join_button_click(
    ack: Ack,
    user: DispatchUser,
    client: WebClient,
    respond: Respond,
    db_session: Session,
    context: BoltContext,
):
    """Handles the case join button click event."""
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    if not case:
        message = "Sorry, we can't invite you to this case. The case does not exist."
    elif case.visibility == Visibility.restricted:
        message = "Sorry, we can't invite you to this case. The case's visibility is restricted. Please, reach out to the case assignee if you have any questions."
    elif case.status == CaseStatus.closed:
        message = "Sorry, you can't join this case. The case has already been marked as closed. Please, reach out to the case assignee if you have any questions."
    elif case.status == CaseStatus.escalated:
        conversation_flows.add_incident_participants_to_conversation(
            incident=case.incidents[0],
            participant_emails=[user.email],
            db_session=db_session,
        )
        message = f"The case has already been escalated to incident {case.incidents[0].name}. We've added you to the incident conversation. Please, check your Slack sidebar for the new incident channel."
    else:
        user_id = context["user_id"]
        try:
            client.conversations_invite(channel=case.conversation.channel_id, users=[user_id])
            message = f"Success! We've added you to case {case.name}. Please, check your Slack sidebar for the new case channel."
        except SlackApiError as e:
            if e.response.get("error") == SlackAPIErrorCode.ALREADY_IN_CHANNEL:
                message = f"Sorry, we can't invite you to this case - you're already a member. Search for a channel called {case.name.lower()} in your Slack sidebar."

    respond(text=message, response_type="ephemeral", replace_original=False, delete_original=False)


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
        case_resolution_reason_select(optional=True),
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
        callback_id=CaseEditActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    CaseEditActions.submit,
    middleware=[
        action_context_middleware,
        db_middleware,
        user_middleware,
        modal_submit_middleware,
    ],
)
def handle_edit_submission_event(
    ack: Ack,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
    user: DispatchUser,
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    previous_case = CaseRead.from_orm(case)

    case_priority = None
    if form_data.get(DefaultBlockIds.case_priority_select):
        case_priority = {"name": form_data[DefaultBlockIds.case_priority_select]["name"]}

    case_type = None
    if form_data.get(DefaultBlockIds.case_type_select):
        case_type = {"name": form_data[DefaultBlockIds.case_type_select]["name"]}

    assignee_email = None
    if form_data.get(DefaultBlockIds.case_assignee_select):
        assignee_email = client.users_info(
            user=form_data[DefaultBlockIds.case_assignee_select]["value"]
        )["user"]["profile"]["email"]

    resolution_reason = None
    if form_data.get(DefaultBlockIds.case_resolution_reason_select):
        resolution_reason = form_data[DefaultBlockIds.case_resolution_reason_select]["value"]

    case_in = CaseUpdate(
        title=form_data[DefaultBlockIds.title_input],
        description=form_data[DefaultBlockIds.description_input],
        resolution=form_data[DefaultBlockIds.resolution_input],
        resolution_reason=resolution_reason,
        status=form_data[DefaultBlockIds.case_status_select]["name"],
        visibility=case.visibility,
        case_priority=case_priority,
        case_type=case_type,
    )

    case = case_service.update(db_session=db_session, case=case, case_in=case_in, current_user=user)

    case_flows.case_update_flow(
        case_id=case.id,
        previous_case=previous_case,
        db_session=db_session,
        reporter_email=case.reporter.individual.email if case.reporter else None,
        assignee_email=assignee_email,
        organization_slug=context["subject"].organization_slug,
    )

    return case


@app.action(CaseNotificationActions.resolve, middleware=[button_context_middleware, db_middleware])
def resolve_button_click(
    ack: Ack, body: dict, db_session: Session, context: BoltContext, client: WebClient
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)

    reason = case.resolution_reason
    blocks = [
        (
            case_resolution_reason_select(initial_option={"text": reason, "value": reason})
            if reason
            else case_resolution_reason_select()
        ),
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


@app.action(CaseNotificationActions.triage, middleware=[button_context_middleware, db_middleware])
def triage_button_click(
    ack: Ack, body: dict, db_session: Session, context: BoltContext, client: WebClient
):
    ack()
    case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    # we run the case status transition flow
    case_flows.case_status_transition_flow_dispatcher(
        case=case,
        current_status=CaseStatus.triage,
        db_session=db_session,
        previous_status=case.status,
        organization_slug=context["subject"].organization_slug,
    )
    case.status = CaseStatus.triage
    db_session.commit()

    # we update the ticket
    ticket_flows.update_case_ticket(case=case, db_session=db_session)

    case_flows.update_conversation(case, db_session)


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
    # we get the current case and store it as previous case
    current_case = case_service.get(db_session=db_session, case_id=context["subject"].id)
    previous_case = CaseRead.from_orm(current_case)

    # we update the case with the new resolution, resolution reason and status
    case_in = CaseUpdate(
        title=current_case.title,
        resolution_reason=form_data[DefaultBlockIds.case_resolution_reason_select]["value"],
        resolution=form_data[DefaultBlockIds.resolution_input],
        visibility=current_case.visibility,
        status=CaseStatus.closed,
    )
    updated_case = case_service.update(
        db_session=db_session,
        case=current_case,
        case_in=case_in,
        current_user=user,
    )

    # we run the case update flow
    case_flows.case_update_flow(
        case_id=updated_case.id,
        previous_case=previous_case,
        db_session=db_session,
        reporter_email=updated_case.reporter.individual.email if updated_case.reporter else None,
        assignee_email=updated_case.assignee.individual.email if updated_case.assignee else None,
        organization_slug=context["subject"].organization_slug,
    )

    # we update the case notification with the resolution, resolution reason and status
    blocks = create_case_message(case=updated_case, channel_id=context["subject"].channel_id)
    client.chat_update(
        blocks=blocks,
        ts=updated_case.conversation.thread_id,
        channel=updated_case.conversation.channel_id,
    )


@app.shortcut(CaseShortcutCallbacks.report, middleware=[db_middleware, shortcut_context_middleware])
def report_issue(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
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
                    text="Cases are meant for triaging events that do not raise to the level of incidents, but can be escalated to incidents if necessary."
                )
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
        title="Open a Case",
        blocks=blocks,
        submit="Report",
        close="Close",
        callback_id=CaseReportActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.action(CaseReportActions.project_select, middleware=[db_middleware, action_context_middleware])
def handle_report_project_select_action(
    ack: Ack,
    body: dict,
    db_session: Session,
    context: BoltContext,
    client: WebClient,
) -> None:
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
        title_input(),
        description_input(),
        project_select(
            db_session=db_session,
            initial_option={"text": project.name, "value": project.id},
            action_id=CaseReportActions.project_select,
            dispatch_action=True,
        ),
        case_type_select(
            db_session=db_session,
            initial_option=None,
            project_id=project.id,
            action_id=CaseReportActions.case_type_select,
            dispatch_action=True,
        ),
        Context(
            elements=[
                MarkdownText(
                    text="💡 Case Types determine the initial assignee based on their configured on-call schedule."
                )
            ]
        ),
    ]

    modal = Modal(
        title="Open a Case",
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


@app.action(
    CaseReportActions.case_type_select,
    middleware=[
        db_middleware,
        action_context_middleware,
    ],
)
def handle_report_case_type_select_action(
    ack: Ack,
    body: dict,
    db_session: Session,
    context: BoltContext,
    client: WebClient,
) -> None:
    ack()
    values = body["view"]["state"]["values"]

    project_id = values[DefaultBlockIds.project_select][CaseReportActions.project_select][
        "selected_option"
    ]["value"]

    case_type_id = values[DefaultBlockIds.case_type_select][CaseReportActions.case_type_select][
        "selected_option"
    ]["value"]

    project = project_service.get(
        db_session=db_session,
        project_id=project_id,
    )

    case_type = case_type_service.get(
        db_session=db_session,
        case_type_id=case_type_id,
    )

    assignee_email = None
    assignee_slack_id = None
    oncall_service_name = None
    service_url = None

    if case_type.oncall_service:
        assignee_email = service_flows.resolve_oncall(
            service=case_type.oncall_service, db_session=db_session
        )
        oncall_service_name = case_type.oncall_service.name

        oncall_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=project.id, plugin_type="oncall"
        )
        if not oncall_plugin:
            log.debug("Unable to send email since oncall plugin is not active.")
        else:
            service_url = oncall_plugin.instance.get_service_url(
                case_type.oncall_service.external_id
            )

    if assignee_email:
        # Get the Slack user ID for the assignee
        try:
            assignee_slack_id = client.users_lookupByEmail(email=assignee_email)["user"]["id"]
        except SlackApiError:
            log.error(f"Failed to find Slack user for email: {assignee_email}")
            assignee_slack_id = None

    blocks = [
        title_input(),
        description_input(),
        project_select(
            db_session=db_session,
            initial_option={"text": project.name, "value": project.id},
            action_id=CaseReportActions.project_select,
            dispatch_action=True,
        ),
        case_type_select(
            db_session=db_session,
            initial_option={"text": case_type.name, "value": case_type.id},
            project_id=project.id,
            action_id=CaseReportActions.case_type_select,
            dispatch_action=True,
        ),
        Context(
            elements=[
                MarkdownText(
                    text="💡 Case Types determine the initial assignee based on their configured on-call schedule."
                )
            ]
        ),
    ]

    # Create a new assignee_select block with a unique block_id
    new_block_id = f"{DefaultBlockIds.case_assignee_select}_{case_type_id}"
    blocks.append(
        assignee_select(
            initial_user=assignee_slack_id if assignee_slack_id else None,
            action_id=CaseReportActions.assignee_select,
            block_id=new_block_id,
        ),
    )

    # Conditionally add context blocks
    if oncall_service_name and assignee_email:
        if service_url:
            oncall_text = (
                f"👩‍🚒 {assignee_email} is on-call for <{service_url}|{oncall_service_name}>"
            )
        else:
            oncall_text = f"👩‍🚒 {assignee_email} is on-call for {oncall_service_name}"

        blocks.extend(
            [
                Context(elements=[MarkdownText(text=oncall_text)]),
                Divider(),
                Context(
                    elements=[
                        MarkdownText(
                            text="Not who you're looking for? You can override the assignee for this case."
                        )
                    ]
                ),
            ]
        )
    else:
        blocks.extend(
            [
                Context(
                    elements=[
                        MarkdownText(
                            text="There is no on-call service associated with this case type."
                        )
                    ]
                ),
                Context(elements=[MarkdownText(text="Please select an assignee for this case.")]),
            ]
        )

    blocks.append(
        case_priority_select(
            db_session=db_session,
            project_id=project.id,
            initial_option=None,
            optional=True,
            block_id=None,  # ensures state is reset
        ),
    )

    modal = Modal(
        title="Open a Case",
        blocks=blocks,
        submit="Report",
        close="Close",
        callback_id=CaseReportActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


def ack_report_case_submission_event(ack: Ack) -> None:
    """Handles the report case submission event acknowledgment."""
    modal = Modal(
        title="Open a Case",
        close="Close",
        blocks=[Section(text="Creating case resources...")],
    ).build()
    ack(response_action="update", view=modal)


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
    ack_report_case_submission_event(ack=ack)

    case_priority = None
    if form_data.get(DefaultBlockIds.case_priority_select):
        case_priority = {"name": form_data[DefaultBlockIds.case_priority_select]["name"]}

    case_type = None
    if form_data.get(DefaultBlockIds.case_type_select):
        case_type = {"name": form_data[DefaultBlockIds.case_type_select]["name"]}

    assignee_block_id = next(
        (key for key in form_data.keys() if key.startswith(DefaultBlockIds.case_assignee_select)),
        None,
    )

    if not assignee_block_id:
        raise ValueError("Assignee block not found in form data")

    assignee_email = client.users_info(user=form_data[assignee_block_id]["value"])["user"][
        "profile"
    ]["email"]

    case_in = CaseCreate(
        title=form_data[DefaultBlockIds.title_input],
        description=form_data[DefaultBlockIds.description_input],
        status=CaseStatus.new,
        case_priority=case_priority,
        case_type=case_type,
        dedicated_channel=True,
        reporter=ParticipantUpdate(individual=IndividualContactRead(email=user.email)),
        assignee=ParticipantUpdate(individual=IndividualContactRead(email=assignee_email)),
    )

    case = case_service.create(db_session=db_session, case_in=case_in, current_user=user)

    modal = Modal(
        title="Case Created",
        close="Close",
        blocks=[Section(text="Running case execution flows...")],
    ).build()

    result = client.views_update(
        view_id=body["view"]["id"],
        trigger_id=body["trigger_id"],
        view=modal,
    )

    case_flows.case_new_create_flow(
        case_id=case.id,
        db_session=db_session,
        organization_slug=context["subject"].organization_slug,
    )

    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        trigger_id=result["trigger_id"],
        title="Case Created",
        message="Case created successfully.",
    )


@app.action(
    SignalEngagementActions.approve,
    middleware=[
        engagement_button_context_middleware,
        db_middleware,
        user_middleware,
    ],
)
def engagement_button_approve_click(
    ack: Ack,
    body: dict,
    db_session: Session,
    context: BoltContext,
    client: WebClient,
    user: DispatchUser,
):
    ack()

    # Engaged user is extracted from the context of the engagement button, which stores the email
    # address of the user who was engaged, and is parsed by the engagement_button_context_middleware.
    engaged_user = context["subject"].user

    user_who_clicked_button = user

    # We check the role of the user who clicked the button to ensure they are authorized to approve
    role = user_who_clicked_button.get_organization_role(
        organization_slug=context["subject"].organization_slug
    )

    # If the user who clicked the button is not the enaged user or a Dispatch admin,
    # we return a modal informing them that they are not authorized to approve the signal.
    if engaged_user != user_who_clicked_button.email and role not in (
        UserRoles.admin,
        UserRoles.owner,
    ):
        modal = Modal(
            title="Not Authorized",
            close="Close",
            blocks=[
                Section(
                    text=f"Sorry, only {engaged_user} or Dispatch administrators can approve this signal."
                )
            ],
        ).build()
        return client.views_open(trigger_id=body["trigger_id"], view=modal)

    engagement = signal_service.get_signal_engagement(
        db_session=db_session,
        signal_engagement_id=context["subject"].engagement_id,
    )

    mfa_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=context["subject"].project_id, plugin_type="auth-mfa"
    )

    require_mfa = engagement.require_mfa if engagement else True
    mfa_enabled = True if mfa_plugin and require_mfa else False

    blocks = [
        Section(text="Confirm that this is expected and that it is not suspicious behavior."),
        Divider(),
        description_input(label="Additional Context", optional=False),
    ]

    if mfa_enabled:
        blocks.append(Section(text=" "))
        blocks.append(
            Context(
                elements=[
                    MarkdownText(
                        text="💡 After submission, you will be asked to validate your identity by completing a Multi-Factor Authentication challenge."
                    )
                ]
            ),
        )

    modal = Modal(
        submit="Submit",
        close="Cancel",
        title="Confirmation",
        callback_id=SignalEngagementActions.approve_submit,
        private_metadata=context["subject"].json(),
        blocks=blocks,
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_mfa_required_submission_event(
    ack: Ack, mfa_enabled: bool, challenge_url: str | None = None
) -> None:
    """Handles the add engagement submission event acknowledgement."""

    if mfa_enabled:
        mfa_text = (
            "🔐 To complete this action, you need to verify your identity through Multi-Factor Authentication (MFA).\n\n"
            f"Please <{challenge_url}|click here> to open the MFA verification page."
        )
    else:
        mfa_text = "✅ No additional verification required. You can proceed with the confirmation."

    blocks = [
        Section(text=mfa_text),
        Divider(),
        Context(
            elements=[
                MarkdownText(
                    text="💡 This step protects against unauthorized confirmation if your account is compromised."
                )
            ]
        ),
    ]

    modal = Modal(
        title="Confirm Your Identity",
        close="Cancel",
        blocks=blocks,
    ).build()

    ack(response_action="update", view=modal)


@app.view(
    SignalEngagementActions.approve_submit,
    middleware=[
        action_context_middleware,
        db_middleware,
        user_middleware,
    ],
)
def handle_engagement_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    user: DispatchUser,
) -> None:
    """Handles the add engagement submission event."""
    metadata = json.loads(body["view"]["private_metadata"])
    engaged_user: str = metadata["user"]

    # we reassign for clarity
    user_who_clicked_button = user

    engagement = signal_service.get_signal_engagement(
        db_session=db_session,
        signal_engagement_id=metadata["engagement_id"],
    )

    mfa_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=context["subject"].project_id, plugin_type="auth-mfa"
    )

    require_mfa = engagement.require_mfa if engagement else True
    mfa_enabled = True if mfa_plugin and require_mfa else False

    challenge, challenge_url = mfa_plugin.instance.create_mfa_challenge(
        action="signal-engagement-confirmation",
        current_user=user,
        db_session=db_session,
        project_id=context["subject"].project_id,
    )

    ack_mfa_required_submission_event(ack=ack, mfa_enabled=mfa_enabled, challenge_url=challenge_url)

    case = case_service.get(db_session=db_session, case_id=metadata["id"])
    signal_instance = (
        signal_service.get_signal_instance(
            db_session=db_session, signal_instance_id=UUID(metadata["signal_instance_id"])
        )
        if metadata["signal_instance_id"]
        else None
    )
    # Get context provided by the user
    context_from_user = body["view"]["state"]["values"][DefaultBlockIds.description_input][
        DefaultBlockIds.description_input
    ]["value"]

    # wait for the mfa challenge
    response = mfa_plugin.instance.wait_for_challenge(
        challenge_id=challenge.challenge_id,
        db_session=db_session,
    )
    if response == MfaChallengeStatus.APPROVED:
        send_engagement_response(
            case=case,
            client=client,
            context_from_user=context_from_user,
            db_session=db_session,
            engagement=engagement,
            engaged_user=engaged_user,
            response=response,
            signal_instance=signal_instance,
            user=user_who_clicked_button,
            view_id=body["view"]["id"],
            thread_id=context["subject"].thread_id,
        )
        db_session.commit()
        return
    else:
        return send_engagement_response(
            case=case,
            client=client,
            context_from_user=context_from_user,
            db_session=db_session,
            engagement=engagement,
            engaged_user=engaged_user,
            response=response,
            signal_instance=signal_instance,
            user=user_who_clicked_button,
            view_id=body["view"]["id"],
            thread_id=context["subject"].thread_id,
        )


def send_engagement_response(
    case: Case,
    client: WebClient,
    context_from_user: str,
    db_session: Session,
    engagement: SignalEngagement | None,
    engaged_user: str,
    response: str,
    signal_instance: SignalInstance | None,
    user: DispatchUser,
    view_id: str,
    thread_id: str,
):
    if response == MfaChallengeStatus.APPROVED:
        title = "Approve"
        text = "Confirmation... Success!"
        message_text = f"{engaged_user} provided the following context:\n```{context_from_user}```"
        engagement_status = SignalEngagementStatus.approved
    else:
        title = "MFA Failed"
        engagement_status = SignalEngagementStatus.denied

        if response == MfaChallengeStatus.EXPIRED:
            text = "Confirmation failed, the MFA request timed out. Please, have your MFA device ready to accept the push notification and try again."
        elif response == MfaChallengeStatus.DENIED:
            text = f"User {engaged_user} not found in MFA provider. To validate your identity, please register in Duo and try again."
        else:
            text = "Confirmation failed. You must accept the MFA prompt."

        message_text = f":warning: {engaged_user} attempted to confirm the behavior as expected, but we ran into an error during MFA validation (`{response}`)\n\n{text}\n\n *Context Provided* \n```{context_from_user}```\n\n"

    send_success_modal(
        client=client,
        view_id=view_id,
        title=title,
        message=text,
    )
    client.chat_postMessage(
        text=message_text,
        channel=case.conversation.channel_id,
        thread_ts=case.conversation.thread_id,
    )

    if response == MfaChallengeStatus.APPROVED:
        # We only update engagement message (which removes Confirm/Deny button) for success
        # this allows the user to retry the confirmation if the MFA check failed
        blocks = create_signal_engagement_message(
            case=case,
            channel_id=case.conversation.channel_id,
            engagement=engagement,
            signal_instance=signal_instance,
            user_email=engaged_user,
            engagement_status=engagement_status,
        )
        if signal_instance:
            client.chat_update(
                blocks=blocks,
                channel=case.conversation.channel_id,
                ts=signal_instance.engagement_thread_ts,
            )
            resolve_case(
                case=case,
                channel_id=case.conversation.channel_id,
                client=client,
                db_session=db_session,
                context_from_user=context_from_user,
                user=user,
            )
        else:
            client.chat_update(
                blocks=blocks,
                channel=case.conversation.channel_id,
                ts=thread_id,
            )


def resolve_case(
    case: Case,
    channel_id: str,
    client: WebClient,
    db_session: Session,
    context_from_user: str,
    user: DispatchUser,
) -> None:
    previous_case = CaseRead.from_orm(case)
    case_flows.case_status_transition_flow_dispatcher(
        case=case,
        current_status=CaseStatus.closed,
        db_session=db_session,
        previous_status=case.status,
        organization_slug=case.project.organization.slug,
    )
    case_in = CaseUpdate(
        title=case.title,
        resolution_reason=CaseResolutionReason.user_acknowledge,
        resolution=context_from_user,
        visibility=case.visibility,
        status=CaseStatus.closed,
        closed_at=datetime.utcnow(),
    )
    case = case_service.update(db_session=db_session, case=case, case_in=case_in, current_user=user)

    case_flows.case_update_flow(
        case_id=case.id,
        previous_case=previous_case,
        db_session=db_session,
        reporter_email=case.reporter.individual.email if case.reporter else None,
        assignee_email=case.assignee.individual.email if case.assignee else None,
        organization_slug=case.project.organization.slug,
    )

    blocks = create_case_message(case=case, channel_id=channel_id)
    client.chat_update(
        blocks=blocks, ts=case.conversation.thread_id, channel=case.conversation.channel_id
    )


@app.action(
    SignalEngagementActions.deny,
    middleware=[engagement_button_context_middleware, db_middleware, user_middleware],
)
def engagement_button_deny_click(
    ack: Ack,
    body: dict,
    context: BoltContext,
    client: WebClient,
    user: DispatchUser,
):
    ack()
    engaged_user = context["subject"].user

    role = user.get_organization_role(organization_slug=context["subject"].organization_slug)
    if engaged_user != user.email and role not in (
        UserRoles.admin,
        UserRoles.owner,
    ):
        modal = Modal(
            title="Not Authorized",
            close="Close",
            blocks=[
                Section(
                    text=f"Sorry, only {engaged_user} or Dispatch administrators can deny this signal."
                )
            ],
        ).build()
        return client.views_open(trigger_id=body["trigger_id"], view=modal)

    modal = Modal(
        submit="Submit",
        close="Cancel",
        title="Not expected",
        callback_id=SignalEngagementActions.deny_submit,
        private_metadata=context["subject"].json(),
        blocks=[
            Section(text="Confirm that this is not expected and that the activity is suspicious."),
            Divider(),
            description_input(label="Additional Context", optional=False),
        ],
    ).build()
    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_engagement_deny_submission_event(ack: Ack) -> None:
    """Handles the deny engagement submission event acknowledgement."""
    modal = Modal(
        title="Confirm",
        close="Close",
        blocks=[Section(text="Confirming event is not expected...")],
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    SignalEngagementActions.deny_submit,
    middleware=[
        action_context_middleware,
        db_middleware,
        user_middleware,
    ],
)
def handle_engagement_deny_submission_event(
    ack: Ack,
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    user: DispatchUser,
) -> None:
    """Handles the add engagement submission event."""
    ack_engagement_deny_submission_event(ack=ack)

    metadata = json.loads(body["view"]["private_metadata"])
    engaged_user = metadata["user"]
    case = case_service.get(db_session=db_session, case_id=metadata["id"])
    signal_instance = (
        signal_service.get_signal_instance(
            db_session=db_session, signal_instance_id=UUID(metadata["signal_instance_id"])
        )
        if metadata["signal_instance_id"]
        else None
    )

    engagement = signal_service.get_signal_engagement(
        db_session=db_session,
        signal_engagement_id=metadata["engagement_id"],
    )
    send_success_modal(
        client=client,
        view_id=body["view"]["id"],
        title="Confirm",
        message="Event has been confirmed as not expected.",
    )

    context_from_user = body["view"]["state"]["values"][DefaultBlockIds.description_input][
        DefaultBlockIds.description_input
    ]["value"]

    client.chat_postMessage(
        text=f":warning: {engaged_user} confirmed the behavior was *not expected*.\n\n *Context Provided* \n```{context_from_user}```",
        channel=case.conversation.channel_id,
        thread_ts=case.conversation.thread_id,
    )

    thread_ts = (
        signal_instance.engagement_thread_ts if signal_instance else context["subject"].thread_id
    )
    blocks = create_signal_engagement_message(
        case=case,
        channel_id=case.conversation.channel_id,
        engagement=engagement,
        signal_instance=signal_instance,
        user_email=user.email,
        engagement_status=SignalEngagementStatus.denied,
    )
    client.chat_update(
        blocks=blocks,
        channel=case.conversation.channel_id,
        ts=thread_ts,
    )
