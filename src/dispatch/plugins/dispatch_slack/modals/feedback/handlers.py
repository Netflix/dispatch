from dispatch.incident import service as incident_service
from dispatch.participant import service as participant_service
from dispatch.feedback import service as feedback_service
from dispatch.feedback.models import FeedbackCreate

from dispatch.plugins.dispatch_slack.decorators import slack_background_task
from dispatch.plugins.dispatch_slack.service import (
    send_message,
    send_ephemeral_message,
    open_modal_with_user,
)
from dispatch.plugins.dispatch_slack.modals.common import parse_submitted_form

from .views import rating_feedback_view, RatingFeedbackBlockId


@slack_background_task
def create_rating_feedback_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Creates a modal for rating and providing feedback about an incident."""
    trigger_id = action["trigger_id"]

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    if not incident:
        message = (
            "Sorry, you cannot submit feedback about this incident. The incident does not exist."
        )
        send_ephemeral_message(slack_client, channel_id, user_id, message)
    else:
        modal_create_template = rating_feedback_view(incident=incident)

        open_modal_with_user(
            client=slack_client, trigger_id=trigger_id, modal=modal_create_template
        )


@slack_background_task
def rating_feedback_from_submitted_form(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Adds rating and feeback to incident based on submitted form data."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    participant = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident_id, email=user_email
    )

    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    feedback = parsed_form_data.get(RatingFeedbackBlockId.feedback)
    rating = parsed_form_data.get(RatingFeedbackBlockId.rating)["value"]
    anonymous = parsed_form_data.get(RatingFeedbackBlockId.anonymous)["value"]

    feedback_in = FeedbackCreate(rating=rating, feedback=feedback, project=incident.project)
    feedback = feedback_service.create(db_session=db_session, feedback_in=feedback_in)

    incident.feedback.append(feedback)

    if anonymous == "":
        participant.feedback.append(feedback)
        db_session.add(participant)

    db_session.add(incident)
    db_session.commit()

    send_message(
        client=slack_client,
        conversation_id=user_id,
        text="Thank you for your feedback!",
    )
