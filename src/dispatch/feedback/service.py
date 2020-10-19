from typing import Optional
from fastapi.encoders import jsonable_encoder

from .models import Feedback, FeedbackCreate, FeedbackUpdate


def get(*, db_session, feedback_id: int) -> Optional[Feedback]:
    """Gets a piece of feedback by its id."""
    return db_session.query(Feedback).filter(Feedback.id == feedback_id).one_or_none()


def get_all(*, db_session):
    """Gets all pieces of feedback."""
    return db_session.query(Feedback)


def create(*, db_session, feedback_in: FeedbackCreate) -> Feedback:
    """Creates a new piece of feedback."""
    feedback = Feedback(**feedback_in.dict())
    db_session.add(feedback)
    db_session.commit()
    return feedback


def update(*, db_session, feedback: Feedback, feedback_in: FeedbackUpdate) -> Feedback:
    """Updates a piece of feedback."""
    feedback_data = jsonable_encoder(feedback)
    update_data = feedback_in.dict(skip_defaults=True)

    for field in feedback_data:
        if field in update_data:
            setattr(feedback, field, update_data[field])

    db_session.add(feedback)
    db_session.commit()
    return feedback


def delete(*, db_session, feedback_id: int):
    """Deletes a piece of feedback."""
    feedback = db_session.query(Feedback).filter(Feedback.id == feedback_id).one_or_none()
    db_session.delete(feedback)
    db_session.commit()
