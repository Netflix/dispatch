import logging
from blockkit import (
    Checkboxes,
    Context,
    Input,
    MarkdownText,
    Modal,
    PlainOption,
    PlainTextInput,
    Section,
)
from slack_bolt import Ack, BoltContext, Respond
from slack_sdk.web.client import WebClient
from sqlalchemy.orm import Session
from datetime import datetime

from dispatch.auth.models import DispatchUser
from dispatch.feedback.incident import service as incident_feedback_service
from dispatch.feedback.incident.enums import FeedbackRating
from dispatch.feedback.incident.models import FeedbackCreate
from dispatch.feedback.service import service as feedback_service
from dispatch.individual import service as individual_service
from dispatch.feedback.service.models import ServiceFeedbackRating, ServiceFeedbackCreate
from dispatch.incident import service as incident_service
from dispatch.participant import service as participant_service
from dispatch.feedback.service.reminder import service as reminder_service
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.fields import static_select_block
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    button_context_middleware,
    db_middleware,
    modal_submit_middleware,
    user_middleware,
)

from .enums import (
    IncidentFeedbackNotificationActionIds,
    IncidentFeedbackNotificationActions,
    IncidentFeedbackNotificationBlockIds,
    ServiceFeedbackNotificationActionIds,
    ServiceFeedbackNotificationActions,
    ServiceFeedbackNotificationBlockIds,
)
from dispatch.messaging.strings import (
    ONCALL_SHIFT_FEEDBACK_RECEIVED,
    MessageType,
)

log = logging.getLogger(__file__)


def configure(config):
    """Placeholder configure function."""
    pass


# Incident Feedback


def rating_select(
    action_id: str = IncidentFeedbackNotificationActionIds.rating_select,
    block_id: str = IncidentFeedbackNotificationBlockIds.rating_select,
    initial_option: dict = None,
    label: str = "Rate your experience",
    **kwargs,
):
    rating_options = [{"text": r.value, "value": r.value} for r in FeedbackRating]
    return static_select_block(
        action_id=action_id,
        block_id=block_id,
        initial_option=initial_option,
        label=label,
        options=rating_options,
        placeholder="Select a rating",
        **kwargs,
    )


def feedback_input(
    action_id: str = IncidentFeedbackNotificationActionIds.feedback_input,
    block_id: str = IncidentFeedbackNotificationBlockIds.feedback_input,
    initial_value: str = None,
    label: str = "Give us feedback",
    **kwargs,
):
    return Input(
        block_id=block_id,
        element=PlainTextInput(
            action_id=action_id,
            initial_value=initial_value,
            multiline=True,
            placeholder="How would you describe your experience?",
        ),
        label=label,
        **kwargs,
    )


def anonymous_checkbox(
    action_id: str = IncidentFeedbackNotificationActionIds.anonymous_checkbox,
    block_id: str = IncidentFeedbackNotificationBlockIds.anonymous_checkbox,
    initial_value: str = None,
    label: str = "Check the box if you wish to provide your feedback anonymously",
    **kwargs,
):
    options = [PlainOption(text="Anonymize my feedback", value="anonymous")]
    return Input(
        block_id=block_id,
        element=Checkboxes(options=options, action_id=action_id),
        label=label,
        optional=True,
        **kwargs,
    )


@app.action(
    IncidentFeedbackNotificationActions.provide,
    middleware=[button_context_middleware, db_middleware],
)
def handle_incident_feedback_direct_message_button_click(
    ack: Ack,
    body: dict,
    client: WebClient,
    respond: Respond,
    db_session: Session,
    context: BoltContext,
):
    """Handles the feedback button in the feedback direct message."""
    ack()
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    if not incident:
        message = (
            "Sorry, you cannot submit feedback about this incident. The incident does not exist."
        )
        respond(message=message, ephemeral=True)
        return

    blocks = [
        Context(
            elements=[
                MarkdownText(text="Use this form to rate your experience about the incident.")
            ]
        ),
        rating_select(),
        feedback_input(),
        anonymous_checkbox(),
    ]

    modal = Modal(
        title="Incident Feedback",
        blocks=blocks,
        submit="Submit",
        close="Cancel",
        callback_id=IncidentFeedbackNotificationActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_incident_feedback_submission_event(ack: Ack) -> None:
    """Handles the feedback submission event acknowledgement."""
    modal = Modal(
        title="Incident Feedback", close="Close", blocks=[Section(text="Submitting feedback...")]
    ).build()
    ack(response_action="update", view=modal)


@app.view(
    IncidentFeedbackNotificationActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
def handle_incident_feedback_submission_event(
    ack: Ack,
    body: dict,
    context: BoltContext,
    user: DispatchUser,
    client: WebClient,
    db_session: Session,
    form_data: dict,
):
    # TODO: handle multiple organizations during submission
    ack_incident_feedback_submission_event(ack=ack)
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    feedback = form_data.get(IncidentFeedbackNotificationBlockIds.feedback_input, "")
    rating = form_data.get(IncidentFeedbackNotificationBlockIds.rating_select, {}).get("value")

    feedback_in = FeedbackCreate(
        rating=rating, feedback=feedback, project=incident.project, incident=incident
    )
    feedback = incident_feedback_service.create(db_session=db_session, feedback_in=feedback_in)
    incident.feedback.append(feedback)

    # we only really care if this exists, if it doesn't then flag is false
    if not form_data.get(IncidentFeedbackNotificationBlockIds.anonymous_checkbox):
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].id, email=user.email
        )
        participant.feedback.append(feedback)
        db_session.add(participant)

    db_session.add(incident)
    db_session.commit()

    modal = Modal(
        title="Incident Feedback",
        close="Close",
        blocks=[Section(text="Submitting feedback... Success!")],
    ).build()

    client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )


# Oncall Shift Feedback


def oncall_shift_feeback_rating_select(
    action_id: str = ServiceFeedbackNotificationActionIds.rating_select,
    block_id: str = ServiceFeedbackNotificationBlockIds.rating_select,
    initial_option: dict = None,
    label: str = "When you consider the whole of the past shift, how much 'mental and emotional effort' did you dedicate toward incident response?",
    **kwargs,
):
    rating_options = [{"text": r.value, "value": r.value} for r in ServiceFeedbackRating]
    return static_select_block(
        action_id=action_id,
        block_id=block_id,
        initial_option=initial_option,
        label=label,
        options=rating_options,
        placeholder="Select a rating",
        **kwargs,
    )


def oncall_shift_feedback_hours_input(
    action_id: str = ServiceFeedbackNotificationActionIds.hours_input,
    block_id: str = ServiceFeedbackNotificationBlockIds.hours_input,
    initial_value: str = None,
    label: str = "Please estimate the number of 'off hours' you spent on incident response tasks during this shift.",
    placeholder: str = "Provide a number of hours",
    **kwargs,
):
    return Input(
        block_id=block_id,
        element=PlainTextInput(
            action_id=action_id,
            initial_value=initial_value,
            multiline=False,
            placeholder=placeholder,
        ),
        label=label,
        **kwargs,
    )


def oncall_shift_feedback_input(
    action_id: str = ServiceFeedbackNotificationActionIds.feedback_input,
    block_id: str = ServiceFeedbackNotificationBlockIds.feedback_input,
    initial_value: str = None,
    label: str = "Describe your experience.",
    **kwargs,
):
    return Input(
        block_id=block_id,
        element=PlainTextInput(
            action_id=action_id,
            initial_value=initial_value,
            multiline=True,
            placeholder="How would you describe your experience?",
        ),
        optional=True,
        label=label,
        **kwargs,
    )


def oncall_shift_feeback_anonymous_checkbox(
    action_id: str = ServiceFeedbackNotificationActionIds.anonymous_checkbox,
    block_id: str = ServiceFeedbackNotificationBlockIds.anonymous_checkbox,
    initial_value: str = None,
    label: str = "Check this box if you wish to provide your feedback anonymously.",
    **kwargs,
):
    options = [PlainOption(text="Anonymize my feedback", value="anonymous")]
    return Input(
        block_id=block_id,
        element=Checkboxes(options=options, action_id=action_id),
        label=label,
        optional=True,
        **kwargs,
    )


@app.action(
    ServiceFeedbackNotificationActions.provide,
    middleware=[db_middleware],
)
def handle_oncall_shift_feedback_direct_message_button_click(
    ack: Ack,
    body: dict,
    client: WebClient,
    respond: Respond,
    db_session: Session,
    context: BoltContext,
):
    """Handles the feedback button in the oncall shift feedback direct message."""
    ack()

    metadata = body["actions"][0]["value"]

    blocks = [
        Context(
            elements=[
                MarkdownText(
                    text="Help us understand the impact of your on-call shift. Use this form to provide feedback."
                )
            ]
        ),
        oncall_shift_feeback_rating_select(),
        oncall_shift_feedback_hours_input(),
        oncall_shift_feedback_input(),
        oncall_shift_feeback_anonymous_checkbox(),
    ]

    modal = Modal(
        title="Oncall Shift Feedback",
        blocks=blocks,
        submit="Submit",
        close="Cancel",
        callback_id=ServiceFeedbackNotificationActions.submit,
        private_metadata=metadata,
    ).build()

    client.views_open(trigger_id=body["trigger_id"], view=modal)


def ack_oncall_shift_feedback_submission_event(ack: Ack) -> None:
    """Handles the oncall shift feedback submission event acknowledgement."""
    modal = Modal(
        title="Oncall Shift Feedback",
        close="Close",
        blocks=[Section(text="Submitting feedback...")],
    ).build()
    ack(response_action="update", view=modal)


def ack_with_error(ack: Ack) -> None:
    """Handles the oncall shift feedback submission form validation."""
    ack(
        response_action="errors",
        errors={
            ServiceFeedbackNotificationBlockIds.hours_input: "The number of hours field must be numeric"
        },
    )


@app.view(
    ServiceFeedbackNotificationActions.submit,
    middleware=[db_middleware, user_middleware, modal_submit_middleware],
)
def handle_oncall_shift_feedback_submission_event(
    ack: Ack,
    body: dict,
    context: BoltContext,
    user: DispatchUser,
    client: WebClient,
    db_session: Session,
    form_data: dict,
):
    hours = form_data.get(ServiceFeedbackNotificationBlockIds.hours_input, "")
    if not hours.replace(".", "", 1).isdigit():
        ack_with_error(ack=ack)
        return

    ack_oncall_shift_feedback_submission_event(ack=ack)

    feedback = form_data.get(ServiceFeedbackNotificationBlockIds.feedback_input, "")
    rating = form_data.get(ServiceFeedbackNotificationBlockIds.rating_select, {}).get("value")

    # metadata is organization_slug|project_id|schedule_id|shift_end_at|reminder_id
    metadata = body["view"]["private_metadata"].split("|")
    project_id = metadata[1]
    schedule_id = metadata[2]
    shift_end_raw = metadata[3]
    shift_end_at = (
        datetime.strptime(shift_end_raw, "%Y-%m-%dT%H:%M:%SZ")
        if "T" in shift_end_raw
        else datetime.strptime(shift_end_raw, "%Y-%m-%d %H:%M:%S")
    )
    # if there's a reminder id, delete the reminder
    if len(metadata) > 4:
        reminder_id = metadata[4]
        if reminder_id.isnumeric():
            reminder_service.delete(db_session=db_session, reminder_id=reminder_id)

    individual = (
        None
        if form_data.get(ServiceFeedbackNotificationBlockIds.anonymous_checkbox)
        else individual_service.get_by_email_and_project(
            db_session=db_session, email=user.email, project_id=project_id
        )
    )

    project = project_service.get(db_session=db_session, project_id=project_id)

    service_feedback = ServiceFeedbackCreate(
        feedback=feedback,
        hours=hours,
        individual=individual,
        rating=ServiceFeedbackRating(rating),
        schedule=schedule_id,
        shift_end_at=shift_end_at,
        shift_start_at=None,
        project=project,
    )

    service_feedback = feedback_service.create(
        db_session=db_session, service_feedback_in=service_feedback
    )

    modal = Modal(
        title="Oncall Shift Feedback",
        close="Close",
        blocks=[Section(text="Submitting feedback... Success!")],
    ).build()

    client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="conversation"
    )

    if plugin:
        notification_text = "Oncall Shift Feedback Received"
        notification_template = ONCALL_SHIFT_FEEDBACK_RECEIVED
        items = [
            {
                "shift_end_at": shift_end_at,
            }
        ]
        try:
            plugin.instance.send_direct(
                user.email,
                notification_text,
                notification_template,
                MessageType.service_feedback,
                items=items,
            )
        except Exception as e:
            log.exception(e)
