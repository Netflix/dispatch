from typing import List, Optional
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder

from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service

from .models import Notification, NotificationCreate, NotificationUpdate


def get(*, db_session, notification_id: int) -> Optional[Notification]:
    """Gets a notifcation by id."""
    return db_session.query(Notification).filter(Notification.id == notification_id).one_or_none()


def get_all(*, db_session):
    """Gets all notifications."""
    return db_session.query(Notification)


def create(*, db_session, notification_in: NotificationCreate) -> Notification:
    """Creates a new notification."""
    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, name=n.name)
        for n in notification_in.incident_types
    ]
    incident_priorities = [
        incident_priority_service.get_by_name(db_session=db_session, name=n.name)
        for n in notification_in.incident_priorities
    ]

    notification = Notification(
        **notification_in.dict(exclude={"incident_types", "incident_priorities"}),
        incident_types=incident_types,
        incident_priorities=incident_priorities,
    )

    db_session.add(notification)
    db_session.commit()
    return notification


def update(
    *, db_session, notification: Notification, notification_in: NotificationUpdate
) -> Notification:
    """Updates a notification."""
    notification_data = jsonable_encoder(notification)

    incident_types = [
        incident_type_service.get_by_name(db_session=db_session, name=n.name)
        for n in notification_in.incident_types
    ]
    incident_priorities = [
        incident_priority_service.get_by_name(db_session=db_session, name=n.name)
        for n in notification_in.incident_priorities
    ]
    update_data = notification_in.dict(
        skip_defaults=True, exclude={"incident_types", "incident_priorities"}
    )

    for field in notification_data:
        if field in update_data:
            setattr(notification, field, update_data[field])

    notification.incident_types = incident_types
    notification.incident_priorities = incident_priorities
    db_session.add(notification)
    db_session.commit()
    return notification


def delete(*, db_session, notification_id: int):
    """Deletes a notification."""
    notification = (
        db_session.query(Notification).filter(Notification.id == notification_id).one_or_none()
    )
    db_session.delete(notification)
    db_session.commit()
