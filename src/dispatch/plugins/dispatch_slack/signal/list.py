import json

from blockkit import (
    Actions,
    Button,
    Context,
    Divider,
    MarkdownText,
    Modal,
    Section,
)
from slack_bolt import Ack, BoltContext
from slack_sdk.web.client import WebClient
from sqlalchemy.orm import Session

from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.case.enums import (
    CasePaginateActions,
    SignalNotificationActions,
)
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    db_middleware,
)
from dispatch.plugins.dispatch_slack.models import (
    SignalSubjects,
    SubjectMetadata,
)
from dispatch.project import service as project_service
from dispatch.signal import service as signal_service


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
