import logging

from typing import List, Optional, Type

from dispatch.database.core import Base
from dispatch.models import PrimaryKey
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service
from dispatch.search_filter import service as search_filter_service

from .models import Notification, NotificationCreate, NotificationUpdate


log = logging.getLogger(__name__)


def get(*, db_session, notification_id: int) -> Optional[Notification]:
    """Gets a notifcation by id."""
    return db_session.query(Notification).filter(Notification.id == notification_id).one_or_none()


def get_all(*, db_session):
    """Gets all notifications."""
    return db_session.query(Notification)


def get_all_enabled(*, db_session, project_id: int) -> Optional[List[Notification]]:
    """Gets all enabled notifications."""
    return (
        db_session.query(Notification)
        .filter(Notification.enabled == True)  # noqa Flake8 E712
        .filter(Notification.project_id == project_id)
    ).all()


def get_overdue_evergreen_notifications(
    *, db_session, project_id: int
) -> List[Optional[Notification]]:
    """Returns all notifications that have not had a recent evergreen notification."""
    query = (
        db_session.query(Notification)
        .filter(Notification.project_id == project_id)
        .filter(Notification.evergreen == True)  # noqa
        .filter(Notification.overdue == True)  # noqa
    )
    return query.all()


def create(*, db_session, notification_in: NotificationCreate) -> Notification:
    """Creates a new notification."""
    filters = []
    if notification_in.filters:
        filters = [
            search_filter_service.get(db_session=db_session, search_filter_id=f.id)
            for f in notification_in.filters
        ]

    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=notification_in.project
    )

    notification = Notification(
        **notification_in.dict(exclude={"filters", "project"}), filters=filters, project=project
    )

    db_session.add(notification)
    db_session.commit()
    return notification


def update(
    *, db_session, notification: Notification, notification_in: NotificationUpdate
) -> Notification:
    """Updates a notification."""
    notification_data = notification.dict()
    update_data = notification_in.dict(
        skip_defaults=True,
        exclude={"filters"},
    )

    for field in notification_data:
        if field in update_data:
            setattr(notification, field, update_data[field])

    if notification_in.filters is not None:
        filters = [
            search_filter_service.get(db_session=db_session, search_filter_id=f.id)
            for f in notification_in.filters
        ]
        notification.filters = filters

    db_session.commit()
    return notification


def delete(*, db_session, notification_id: int):
    """Deletes a notification."""
    notification = (
        db_session.query(Notification).filter(Notification.id == notification_id).one_or_none()
    )
    db_session.delete(notification)
    db_session.commit()


def send(
    *, db_session, project_id: int, notification: Notification, notification_params: dict = None
):
    """Send a notification via plugin."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type=notification.type
    )

    if plugin:
        # Can raise exception "tenacity.RetryError: RetryError". (Email may still go through).
        try:
            plugin.instance.send(
                notification.target,
                notification_params["text"],
                notification_params["template"],
                notification_params["type"],
                **notification_params["kwargs"],
            )
        except Exception as e:
            log.exception(e)
            log.error(f"Error in sending {notification_params['type']}: {e}")
            log.exception(e)
    else:
        log.warning(
            f"Notification {notification.name} not sent. No {notification.type} plugin is active."
        )


def filter_and_send(
    *,
    db_session,
    project_id: PrimaryKey,
    class_instance: Type[Base],
    notification_params: dict = None,
):
    """Sends notifications."""
    notifications = get_all_enabled(db_session=db_session, project_id=project_id)
    for notification in notifications:
        for search_filter in notification.filters:
            match = search_filter_service.match(
                db_session=db_session,
                subject=search_filter.subject,
                filter_spec=search_filter.expression,
                class_instance=class_instance,
            )
            if match:
                send(
                    db_session=db_session,
                    project_id=project_id,
                    notification=notification,
                    notification_params=notification_params,
                )

        if not notification.filters:
            send(
                db_session=db_session,
                project_id=project_id,
                notification=notification,
                notification_params=notification_params,
            )
