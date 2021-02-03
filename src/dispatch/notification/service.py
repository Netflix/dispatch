import logging

from typing import List, Optional, Type

from fastapi.encoders import jsonable_encoder

from dispatch.database import Base
from dispatch.plugin import service as plugin_service
from dispatch.search import service as search_service

from .models import Notification, NotificationCreate, NotificationUpdate


log = logging.getLogger(__name__)


def get(*, db_session, notification_id: int) -> Optional[Notification]:
    """Gets a notifcation by id."""
    return db_session.query(Notification).filter(Notification.id == notification_id).one_or_none()


def get_all(*, db_session):
    """Gets all notifications."""
    return db_session.query(Notification)


def get_all_enabled(*, db_session) -> Optional[List[Notification]]:
    """Gets all enabled notifications."""
    return (
        db_session.query(Notification).filter(Notification.enabled == True)  # noqa Flake8 E712
    ).all()


def create(*, db_session, notification_in: NotificationCreate) -> Notification:
    """Creates a new notification."""
    filters = [
        search_service.get(db_session=db_session, search_filter_id=f.id)
        for f in notification_in.filters
    ]

    notification = Notification(
        **notification_in.dict(exclude={"filters"}),
        filters=filters,
    )

    db_session.add(notification)
    db_session.commit()
    return notification


def update(
    *, db_session, notification: Notification, notification_in: NotificationUpdate
) -> Notification:
    """Updates a notification."""
    notification_data = jsonable_encoder(notification)

    filters = [
        search_service.get(db_session=db_session, search_filter_id=f.id)
        for f in notification_in.filters
    ]

    update_data = notification_in.dict(
        skip_defaults=True,
        exclude={"filters"},
    )

    for field in notification_data:
        if field in update_data:
            setattr(notification, field, update_data[field])

    notification.filters = filters
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


def send(*, db_session, notification: Notification, notification_params: dict):
    """Send a notification via plugin."""
    plugin = plugin_service.get_active(db_session=db_session, plugin_type=notification.type)
    if plugin:
        plugin.instance.send(
            notification.target,
            notification_params["text"],
            notification_params["template"],
            notification_params["type"],
            **notification_params["kwargs"],
        )
    else:
        log.warning(
            f"Notification {notification.name} not sent. No {notification.type} plugin is active."
        )


def filter_and_send(*, db_session, class_instance: Type[Base], notification_params: dict):
    """Sends notifications."""
    notifications = get_all_enabled(db_session=db_session)
    for notification in notifications:
        for search_filter in notification.filters:
            match = search_service.match(
                db_session=db_session,
                filter_spec=search_filter.expression,
                class_instance=class_instance,
            )
            if match:
                send(
                    db_session=db_session,
                    notification=notification,
                    notification_params=notification_params,
                )

        if not notification.filters:
            send(
                db_session=db_session,
                notification=notification,
                notification_params=notification_params,
            )
