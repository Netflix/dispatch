from blockkit import Checkboxes, Context, Input, MarkdownText, Modal, PlainTextInput

from dispatch.enums import DispatchEnum
from dispatch.feedback import service as feedback_service
from dispatch.feedback.enums import FeedbackRating
from dispatch.feedback.models import FeedbackCreate
from dispatch.incident import service as incident_service
from dispatch.participant import service as participant_service

from .bolt import app
from .fields import static_select_block
from .middleware import (
    action_context_middleware,
    button_context_middleware,
    db_middleware,
    modal_submit_middleware,
    user_middleware,
)


class FeedbackNotificationBlockIds(DispatchEnum):
    feedback_input = "feedback-notification-feedback-input"
    rating_select = "feedback-notification-rating-select"
    anonymous_checkbox = "feedback-notification-anonymous-checkbox"


class FeedbackNotificationActionIds(DispatchEnum):
    feedback_input = "feedback-notification-feedback-input"
    rating_select = "feedback-notification-rating-select"
    anonymous_checkbox = "feedback-notification-anonymous-checkbox"


class FeedbackNotificationActions(DispatchEnum):
    submit = "feedback-notification-submit"
    provide = "feedback-notification-provide"


def rating_select(
    action_id: str = FeedbackNotificationActionIds.rating_select,
    block_id: str = FeedbackNotificationBlockIds.rating_select,
    initial_option: dict = None,
    label: str = "Rate your experience",
    **kwargs,
):
    return static_select_block(
        action_id=action_id,
        block_id=block_id,
        initial_option=initial_option,
        label=label,
        options=[{"text": r, "value": r} for r in FeedbackRating],
        placeholder="Select a rating",
        **kwargs,
    )


def feedback_input(
    action_id: str = FeedbackNotificationActionIds.feedback_input,
    block_id: str = FeedbackNotificationBlockIds.feedback_input,
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
    action_id: str = FeedbackNotificationActionIds.anonymous_checkbox,
    block_id: str = FeedbackNotificationBlockIds.anonymous_checkbox,
    initial_value: str = None,
    label: str = "Check the box if you wish to provide your feedback anonymously",
    **kwargs,
):
    options = [{"text": "Anonymize my feedback", "value": "anonymous"}]
    return Input(
        block_id=block_id,
        element=Checkboxes(options=options, initial_value=initial_value, action_id=action_id),
        label=label,
        **kwargs,
    )


@app.action(
    FeedbackNotificationActions.provide, middleware=[button_context_middleware, db_middleware]
)
async def provide_feedback_button_click(ack, body, client, respond, db_session, context):
    await ack()
    incident = incident_service.get(
        db_session=db_session, incident_id=context["subject"].incident_id
    )

    if not incident:
        message = (
            "Sorry, you cannot submit feedback about this incident. The incident does not exist."
        )
        await respond(message=message, ephemeral=True)
        return
    blocks = [
        Context(
            elements=[
                MarkdownText(text="Use this form to rate your experiance about the incident.")
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
        callback_id=FeedbackNotificationActions.submit,
        private_metadata=context["subject"].json(),
    ).build()
    await client.views_open(trigger_id=body["trigger_id"], view=modal)


@app.view(
    FeedbackNotificationActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_feedback_submission_event(ack, body, context, db_session, user, client, form_data):
    await ack()
    incident = incident_service.get(
        db_session=db_session, incident_id=context["subject"].incident_id
    )

    feedback = form_data.get(FeedbackNotificationBlockIds.feedback_input)
    rating = form_data.get(FeedbackNotificationBlockIds.rating_select, {}).get("value")

    feedback_in = FeedbackCreate(
        rating=rating, feedback=feedback, project=incident.project, incident=incident
    )
    feedback = feedback_service.create(db_session=db_session, feedback_in=feedback_in)
    incident.feedback.append(feedback)

    # we only really care if this exists, if it doesn't then flag is false
    if not form_data.get(FeedbackNotificationBlockIds.anonymous_checkbox):
        participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=context["subject"].incident_id, email=user.email
        )
        participant.feedback.append(feedback)
        db_session.add(participant)

    db_session.add(incident)
    db_session.commit()

    await client.chat_PostMessage(text="Thank you for your feedback!")
