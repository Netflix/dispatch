from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency

from .models import (
    NotificationCreate,
    NotificationPagination,
    NotificationRead,
    NotificationUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=NotificationPagination)
def get_notifications(*, common: dict = Depends(common_parameters)):
    """
    Get all notifications, or only those matching a given search term.
    """
    return search_filter_sort_paginate(model="Notification", **common)


@router.get("/{notification_id}", response_model=NotificationRead)
def get_notification(*, db_session: Session = Depends(get_db), notification_id: int):
    """
    Get a notification by id.
    """
    notification = get(db_session=db_session, notification_id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="A notification with this id does not exist.")
    return notification


@router.post(
    "",
    response_model=NotificationRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_notification(
    *, db_session: Session = Depends(get_db), notification_in: NotificationCreate
):
    """
    Create a notification.
    """
    notification = create(db_session=db_session, notification_in=notification_in)
    return notification


@router.put(
    "/{notification_id}",
    response_model=NotificationRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_notification(
    *,
    db_session: Session = Depends(get_db),
    notification_id: int,
    notification_in: NotificationUpdate,
):
    """
    Update a notification by id.
    """
    notification = get(db_session=db_session, notification_id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="A notification with this id does not exist.")
    notification = update(
        db_session=db_session, notification=notification, notification_in=notification_in
    )
    return notification


@router.delete(
    "/{notification_id}",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_notification(*, db_session: Session = Depends(get_db), notification_id: int):
    """
    Delete a notification, returning only an HTTP 200 OK if successful.
    """
    notification = get(db_session=db_session, notification_id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="A notification with this id does not exist.")
    delete(db_session=db_session, notification_id=notification_id)
