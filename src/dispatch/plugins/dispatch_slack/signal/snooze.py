from dataclasses import dataclass
from typing import List, Optional

from blockkit import Context, Divider, MarkdownText, Modal, Section
from pydantic import BaseModel, Field
from slack_bolt import Ack, BoltContext
from slack_sdk import WebClient
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.entity import service as entity_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.fields import (
    DefaultBlockIds,
    description_input,
    entity_select,
    relative_date_picker_input,
    title_input,
)
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    button_context_middleware,
    db_middleware,
    modal_submit_middleware,
    user_middleware,
)
from dispatch.plugins.dispatch_slack.models import (
    FormMetadata,
    SignalSubjects,
    SubjectMetadata,
)
from dispatch.signal import service as signal_service
from dispatch.signal.models import (
    Signal,
    SignalInstance,
)

from .enums import SignalNotificationActions, SignalSnoozeActions


class SignalSnoozeData(BaseModel):
    """Data model for signal snooze operations."""

    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    expiration_delta: str
    entity_ids: List[int] = Field(default_factory=list)
    signal_id: int
    project_id: int


@dataclass
class SnoozeContext:
    """Context for snooze operations."""

    db_session: Session
    client: WebClient
    body: dict
    context: BoltContext
    ack: Ack
    user: Optional[DispatchUser] = None
    form_data: Optional[dict] = None


class SnoozeModalBuilder:
    """Builder for snooze-related modals."""

    @staticmethod
    def build_initial_modal(
        db_session: Session,
        signal: Signal,
        subject: SubjectMetadata,
    ) -> dict:
        """Build the initial snooze modal."""
        blocks = [
            Context(elements=[MarkdownText(text=f"{signal.name}")]),
            Divider(),
            title_input(placeholder="A name for your snooze filter."),
            description_input(placeholder="Provide a description for your snooze filter."),
            relative_date_picker_input(label="Expiration"),
        ]

        entity_select_block = entity_select(
            db_session=db_session,
            signal_id=signal.id,
            optional=True,
        )

        if entity_select_block:
            blocks.extend(
                [
                    entity_select_block,
                    Context(
                        elements=[
                            MarkdownText(
                                text="Signals that contain all selected entities will be snoozed for the configured timeframe."
                            )
                        ]
                    ),
                ]
            )

        return Modal(
            title="Snooze Signal",
            blocks=blocks,
            submit="Preview",
            close="Close",
            callback_id=SignalSnoozeActions.preview,
            private_metadata=subject.json(),
        ).build()

    @staticmethod
    def build_preview_modal(
        signal_instances: list[SignalInstance] | None,
        form_data: dict,
        context: BoltContext,
    ) -> dict:
        """Build the preview modal."""
        text = (
            "Examples matching your filter:"
            if signal_instances
            else "No entities selected. All instances of this signal will be snoozed."
            if not form_data.get(DefaultBlockIds.entity_select)
            else "No signals matching your filter."
        )

        blocks = [Context(elements=[MarkdownText(text=text)])]

        if signal_instances:
            for instance in signal_instances[:5]:
                blocks.extend(SnoozeModalBuilder._build_instance_blocks(instance))

        private_metadata = FormMetadata(
            form_data=form_data,
            **context["subject"].dict(),
        ).json()

        return Modal(
            title="Add Snooze",
            submit="Create",
            close="Close",
            blocks=blocks,
            callback_id=SignalSnoozeActions.submit,
            private_metadata=private_metadata,
        ).build()

    @staticmethod
    def _build_instance_blocks(instance: SignalInstance) -> list[Section | Context]:
        """Build blocks for a signal instance preview."""
        return [
            Section(text=instance.signal.name),
            Context(
                elements=[
                    MarkdownText(text=f" Case: {instance.case.name if instance.case else 'N/A'}")
                ]
            ),
            Context(
                elements=[
                    MarkdownText(
                        text=f" Created: {instance.case.created_at if instance.case else 'N/A'}"
                    )
                ]
            ),
        ]


class SnoozeService:
    """Service for handling snooze operations."""

    def __init__(self, context: SnoozeContext):
        self.context = context
        self.db_session = context.db_session

    def handle_button_click(self) -> None:
        """Handle initial snooze button click."""
        self.context.ack()
        subject = self._process_subject()
        signal = self._get_signal(subject.id)
        modal = SnoozeModalBuilder.build_initial_modal(self.db_session, signal, subject)
        self._show_modal(modal)

    def handle_preview(self) -> None:
        """Handle preview request."""
        title = self.context.form_data.get(DefaultBlockIds.title_input)

        if self._is_name_taken(title):
            self._show_name_taken_error(title)
            return

        signal_instances = self._get_preview_instances()
        modal = SnoozeModalBuilder.build_preview_modal(
            signal_instances, self.context.form_data, self.context.context
        )
        self.context.ack(response_action="update", view=modal)

    def handle_submission(self) -> None:
        """Handle final submission."""
        # Delegate to the submission handler from the previous implementation
        pass

    def _process_subject(self) -> SubjectMetadata:
        """Process and validate subject metadata."""
        subject = self.context.context["subject"]
        if subject.type == SignalSubjects.signal_instance:
            instance = signal_service.get_signal_instance(
                db_session=self.db_session, signal_instance_id=subject.id
            )
            subject.id = instance.signal.id
        return subject

    def _get_signal(self, signal_id: int) -> Signal:
        """Get signal by ID."""
        return signal_service.get(db_session=self.db_session, signal_id=signal_id)

    def _is_name_taken(self, title: str) -> bool:
        """Check if filter name is already taken."""
        return bool(
            signal_service.get_signal_filter_by_name(
                db_session=self.db_session,
                project_id=self.context.context["subject"].project_id,
                name=title,
            )
        )

    def _get_preview_instances(self) -> list[SignalInstance] | None:
        """Get preview instances based on selected entities."""
        if not (entity_data := self.context.form_data.get(DefaultBlockIds.entity_select)):
            return None

        entity_ids = [entity["value"] for entity in entity_data]
        return entity_service.get_signal_instances_with_entities(
            db_session=self.db_session,
            signal_id=self.context.context["subject"].id,
            entity_ids=entity_ids,
            days_back=90,
        )

    def _show_modal(self, modal: dict) -> None:
        """Show modal to user."""
        if view_id := self.context.body.get("view", {}).get("id"):
            self.context.client.views_update(view_id=view_id, view=modal)
        else:
            self.context.client.views_open(trigger_id=self.context.body["trigger_id"], view=modal)

    def _show_name_taken_error(self, title: str) -> None:
        """Show error modal for taken names."""
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
        self.context.ack(response_action="update", view=modal)


@app.action(
    SignalNotificationActions.snooze,
    middleware=[
        button_context_middleware,
        db_middleware,
    ],
)
def snooze_button_click(
    ack: Ack, body: dict, client: WebClient, context: BoltContext, db_session: Session
) -> None:
    """Handle snooze button click."""
    SnoozeService(
        SnoozeContext(
            db_session=db_session,
            client=client,
            body=body,
            context=context,
            ack=ack,
        )
    ).handle_button_click()


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
    body: dict,
    client: WebClient,
    context: BoltContext,
    db_session: Session,
    form_data: dict,
) -> None:
    """Handle snooze preview request."""
    SnoozeService(
        SnoozeContext(
            db_session=db_session,
            client=client,
            body=body,
            context=context,
            ack=ack,
            form_data=form_data,
        )
    ).handle_preview()


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
    """Handle final snooze submission."""
    SnoozeService(
        SnoozeContext(
            db_session=db_session,
            client=client,
            body=body,
            context=context,
            ack=ack,
            user=user,
        )
    ).handle_submission()
