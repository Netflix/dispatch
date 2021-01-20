from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder
from typing import Optional

from dispatch.policy import service as policy_service

from .models import Notification, NotificationCreate, NotificationUpdate


def get(*, db_session, notification_id: int) -> Optional[Notification]:
    """Gets a notifcation by id."""
    return db_session.query(Notification).filter(Notification.id == notification_id).one_or_none()


def get_all(*, db_session):
    """Gets all notifications."""
    return db_session.query(Notification)


def create(*, db_session, notification_in: NotificationCreate) -> Notification:
    """Creates a new notification."""
    policy = policy_service.get_by_name(db_session=db_session, text=notification_in.policy.name)

    notification = Notification(
        **notification_in.dict(exclude={"policy"}),
        policy=policy,
    )

    db_session.add(notification)
    db_session.commit()
    return notification


def update(
    *, db_session, notification: Notification, notification_in: NotificationUpdate
) -> Notification:
    """Updates a notification."""
    notification_data = jsonable_encoder(notification)

    policy = policy_service.get_by_name(db_session=db_session, text=notification_in.policy.name)

    update_data = notification_in.dict(
        skip_defaults=True,
        exclude={"policy"},
    )

    for field in notification_data:
        if field in update_data:
            setattr(notification, field, update_data[field])

    notification.policy = policy
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
