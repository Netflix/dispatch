from typing import Optional

from sqlalchemy.orm import Session

from .models import ServiceFeedback, ServiceFeedbackCreate, ServiceFeedbackUpdate


def get(*, service_feedback_id: int, db_session: Session) -> Optional[ServiceFeedback]:
    """Gets a piece of service feedback by its id."""
    return (
        db_session.query(ServiceFeedback)
        .filter(ServiceFeedback.id == service_feedback_id)
        .one_or_none()
    )


def get_all(*, db_session: Session):
    """Gets all pieces of service feedback."""
    return db_session.query(ServiceFeedback)


def create(*, service_feedback_in: ServiceFeedbackCreate, db_session: Session) -> ServiceFeedback:
    """Creates a new piece of service feedback."""

    individual_contact_id = (
        None if not service_feedback_in.individual else service_feedback_in.individual.id
    )

    project_id = None if not service_feedback_in.project else service_feedback_in.project.id

    service_feedback = ServiceFeedback(
        **service_feedback_in.dict(exclude={"individual", "project"}),
        individual_contact_id=individual_contact_id,
        project_id=project_id,
    )
    db_session.add(service_feedback)
    db_session.commit()
    return service_feedback


def update(
    *,
    service_feedback: ServiceFeedback,
    service_feedback_in: ServiceFeedbackUpdate,
    db_session: Session,
) -> ServiceFeedback:
    """Updates a piece of service feedback."""
    service_feedback_data = service_feedback.dict()
    update_data = service_feedback_in.dict(skip_defaults=True)

    for field in service_feedback_data:
        if field in update_data:
            setattr(service_feedback, field, update_data[field])

    db_session.commit()
    return service_feedback


def delete(*, db_session, service_feedback_id: int):
    """Deletes a piece of service feedback."""
    service_feedback = (
        db_session.query(ServiceFeedback)
        .filter(ServiceFeedback.id == service_feedback_id)
        .one_or_none()
    )
    db_session.delete(service_feedback)
    db_session.commit()
