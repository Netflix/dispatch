from typing import List, Optional
from datetime import datetime, timedelta

from .models import (
    ServiceFeedbackReminder,
    ServiceFeedbackReminderUpdate,
)
from dispatch.individual.models import IndividualContact
from dispatch.project.models import Project


def get_all_expired_reminders_by_project_id(
    *, db_session, project_id: int
) -> List[Optional[ServiceFeedbackReminder]]:
    """Returns all expired reminders by project id."""
    return (
        db_session.query(ServiceFeedbackReminder)
        .join(IndividualContact)
        .join(Project)
        .filter(Project.id == project_id)
        .filter(datetime.utcnow() >= ServiceFeedbackReminder.reminder_at - timedelta(minutes=1))
        .all()
    )


def create(*, db_session, reminder_in: ServiceFeedbackReminder) -> ServiceFeedbackReminder:
    """Creates a new service feedback reminder."""
    reminder = ServiceFeedbackReminder(**reminder_in.dict())

    db_session.add(reminder)
    db_session.commit()
    return reminder


def update(
    *, db_session, reminder: ServiceFeedbackReminder, reminder_in: ServiceFeedbackReminderUpdate
) -> ServiceFeedbackReminder:
    """Updates a service feedback reminder."""
    reminder_data = reminder.dict()
    update_data = reminder_in.dict(skip_defaults=True)

    for field in reminder_data:
        if field in update_data:
            setattr(reminder, field, update_data[field])

    db_session.commit()
    return reminder


def delete(*, db_session, reminder_id: int):
    """Deletes a service feedback reminder."""
    reminder = (
        db_session.query(ServiceFeedbackReminder)
        .filter(ServiceFeedbackReminder.id == reminder_id)
        .one_or_none()
    )
    if reminder:
        db_session.delete(reminder)
        db_session.commit()
