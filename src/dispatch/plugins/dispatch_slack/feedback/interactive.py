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

from dispatch.auth.models import DispatchUser
from dispatch.enums import DispatchEnum
from dispatch.feedback import service as feedback_service
from dispatch.feedback.enums import FeedbackRating
from dispatch.feedback.models import FeedbackCreate
from dispatch.incident import service as incident_service
from dispatch.participant import service as participant_service
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
    OncallShiftFeedbackNotificationActionIds,
    OncallShiftFeedbackNotificationActions,
    OncallShiftFeedbackNotificationBlockIds,
)


class OncallShiftFeedbackRating(DispatchEnum):
    no_effort = "No effort"
    little_effort = "Little effort"
    moderate_effort = "Moderate effort"
    lots_of_effort = "Lots of effort"
    very_high_effort = "Very high effort"
    extreme_effort = "Extreme effort, everything I could give"


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

    feedback = form_data.get(IncidentFeedbackNotificationBlockIds.feedback_input)
    rating = form_data.get(IncidentFeedbackNotificationBlockIds.rating_select, {}).get("value")

    feedback_in = FeedbackCreate(
        rating=rating, feedback=feedback, project=incident.project, incident=incident
    )
    feedback = feedback_service.create(db_session=db_session, feedback_in=feedback_in)
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
    action_id: str = OncallShiftFeedbackNotificationActionIds.rating_select,
    block_id: str = OncallShiftFeedbackNotificationBlockIds.rating_select,
    initial_option: dict = None,
    label: str = "When you consider the whole of the past shift, how much 'mental and emotional effort' did you dedicate toward incident response?",
    **kwargs,
):
    rating_options = [{"text": r.value, "value": r.value} for r in OncallShiftFeedbackRating]
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
    action_id: str = OncallShiftFeedbackNotificationActionIds.hours_input,
    block_id: str = OncallShiftFeedbackNotificationBlockIds.hours_input,
    initial_value: str = None,
    label: str = "Please estimate the number of 'off hours' you spent on incident response tasks during this shift. (In this context, 'off hours' are hours outside of your 'normal' desired workday.)",
    placeholder="Provide a number",
    **kwargs,
):
    return Input(
        block_id=block_id,
        element=PlainTextInput(
            action_id=action_id,
            initial_value=initial_value,
            multiline=False,
            # placeholder="How would you describe your experience?",
        ),
        label=label,
        **kwargs,
    )


def oncall_shift_feedback_input(
    action_id: str = OncallShiftFeedbackNotificationActionIds.feedback_input,
    block_id: str = OncallShiftFeedbackNotificationBlockIds.feedback_input,
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


def oncall_shift_feeback_anonymous_checkbox(
    action_id: str = OncallShiftFeedbackNotificationActionIds.anonymous_checkbox,
    block_id: str = OncallShiftFeedbackNotificationBlockIds.anonymous_checkbox,
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
    OncallShiftFeedbackNotificationActions.provide,
    middleware=[button_context_middleware, db_middleware],
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
        callback_id=OncallShiftFeedbackNotificationActions.submit,
        private_metadata=context["subject"].json(),
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


@app.view(
    OncallShiftFeedbackNotificationActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
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
    # TODO: handle multiple organizations during submission
    ack_oncall_shift_feedback_submission_event(ack=ack)
    # incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
    #
    # feedback = form_data.get(OncallShiftFeedbackNotificationBlockIds.feedback_input)
    # rating = form_data.get(OncallShiftFeedbackNotificationBlockIds.rating_select, {}).get("value")
    #
    # feedback_in = FeedbackCreate(
    # 	  rating=rating, feedback=feedback, project=incident.project, incident=incident
    # )
    # feedback = feedback_service.create(db_session=db_session, feedback_in=feedback_in)
    # incident.feedback.append(feedback)
    #
    # # we only really care if this exists, if it doesn't then flag is false
    # if not form_data.get(OncallShiftFeedbackNotificationBlockIds.anonymous_checkbox):
    # 	  participant = participant_service.get_by_incident_id_and_email(
    # 		  db_session=db_session, incident_id=context["subject"].id, email=user.email
    # 	  )
    # 	  participant.feedback.append(feedback)
    # 	  db_session.add(participant)
    #
    # db_session.add(incident)
    # db_session.commit()

    modal = Modal(
        title="Oncall Shift Feedback",
        close="Close",
        blocks=[Section(text="Submitting feedback... Success!")],
    ).build()

    client.views_update(
        view_id=body["view"]["id"],
        view=modal,
    )
