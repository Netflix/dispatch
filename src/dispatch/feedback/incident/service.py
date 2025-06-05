from datetime import datetime, timedelta

from dispatch.incident import service as incident_service
from dispatch.case import service as case_service
from dispatch.incident.models import Incident
from dispatch.case.models import Case
from dispatch.project.models import Project

from .models import Feedback, FeedbackCreate, FeedbackUpdate


def get(*, db_session, feedback_id: int) -> Feedback | None:
    """Gets a piece of feedback by its id."""
    return db_session.query(Feedback).filter(Feedback.id == feedback_id).one_or_none()


def get_all(*, db_session):
    """Gets all pieces of feedback."""
    return db_session.query(Feedback)


def get_all_incident_last_x_hours_by_project_id(
    *, db_session, hours: int = 24, project_id: int
) -> list[Feedback | None]:
    """Returns all feedback provided in the last x hours by project id. Defaults to 24 hours."""
    return (
        db_session.query(Feedback)
        .join(Incident)
        .join(Project)
        .filter(Project.id == project_id)
        .filter(Feedback.created_at >= datetime.utcnow() - timedelta(hours=hours))
        .all()
    )


def get_all_case_last_x_hours_by_project_id(
    *, db_session, hours: int = 24, project_id: int
) -> list[Feedback | None]:
    """Returns all feedback provided in the last x hours by project id. Defaults to 24 hours."""
    return (
        db_session.query(Feedback)
        .join(Case)
        .join(Project)
        .filter(Project.id == project_id)
        .filter(Feedback.created_at >= datetime.utcnow() - timedelta(hours=hours))
        .all()
    )


def create(*, db_session, feedback_in: FeedbackCreate) -> Feedback:
    """Creates a new piece of feedback."""
    if feedback_in.incident:
        incident = incident_service.get(
            db_session=db_session,
            incident_id=feedback_in.incident.id,
        )
        project = incident.project
        case = None
        participant = feedback_in.participant
    else:
        case = case_service.get(
            db_session=db_session,
            case_id=feedback_in.case.id,
        )
        project = case.project
        incident = None
        # Get the participant from the database if it's provided as a dict/model
        participant = None
        if feedback_in.participant:
            from dispatch.participant.service import get as get_participant

            participant = get_participant(
                db_session=db_session, participant_id=feedback_in.participant.id
            )

    # Create feedback with the actual ORM objects, not the Pydantic models
    feedback = Feedback(
        rating=feedback_in.rating,
        feedback=feedback_in.feedback,
        incident=incident,
        case=case,
        project=project,
        participant=participant,
    )
    db_session.add(feedback)
    db_session.commit()
    return feedback


def update(*, db_session, feedback: Feedback, feedback_in: FeedbackUpdate) -> Feedback:
    """Updates a piece of feedback."""
    feedback_data = feedback.dict()
    update_data = feedback_in.dict(exclude_unset=True)

    for field in feedback_data:
        if field in update_data:
            setattr(feedback, field, update_data[field])

    db_session.commit()
    return feedback


def delete(*, db_session, feedback_id: int):
    """Deletes a piece of feedback."""
    feedback = db_session.query(Feedback).filter(Feedback.id == feedback_id).one_or_none()
    db_session.delete(feedback)
    db_session.commit()
