from typing import List, Optional
from datetime import datetime, timedelta

from dispatch.incident import service as incident_service
from dispatch.incident.models import Incident
from dispatch.project.models import Project

from .models import Feedback, FeedbackCreate, FeedbackUpdate


def get(*, db_session, feedback_id: int) -> Optional[Feedback]:
    """Gets a piece of feedback by its id."""
    return db_session.query(Feedback).filter(Feedback.id == feedback_id).one_or_none()


def get_all(*, db_session):
    """Gets all pieces of feedback."""
    return db_session.query(Feedback)


def get_all_last_x_hours_by_project_id(
    *, db_session, hours: int = 24, project_id: int
) -> List[Optional[Feedback]]:
    """Returns all feedback provided in the last x hours by project id. Defaults to 24 hours."""
    return (
        db_session.query(Feedback)
        .join(Incident)
        .join(Project)
        .filter(Project.id == project_id)
        .filter(Feedback.created_at >= datetime.utcnow() - timedelta(hours=hours))
        .all()
    )


def create(*, db_session, feedback_in: FeedbackCreate) -> Feedback:
    """Creates a new piece of feedback."""
    incident = incident_service.get(
        db_session=db_session,
        incident_id=feedback_in.incident.id,
    )
    feedback = Feedback(
        **feedback_in.dict(exclude={"incident"}),
        incident=incident,
    )
    db_session.add(feedback)
    db_session.commit()
    return feedback


def update(*, db_session, feedback: Feedback, feedback_in: FeedbackUpdate) -> Feedback:
    """Updates a piece of feedback."""
    feedback_data = feedback.dict()
    update_data = feedback_in.dict(skip_defaults=True)

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
