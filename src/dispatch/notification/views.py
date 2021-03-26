from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.auth.permissions import AdminPermission, PermissionsDependency
from dispatch.database.core import get_db
from dispatch.database.service import search_filter_sort_paginate

from .models import (
    NotificationCreate,
    NotificationPagination,
    NotificationRead,
    NotificationUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("/", response_model=NotificationPagination)
def get_notifications(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
):
    """
    Get all notifications, or only those matching a given search term.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Notification",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


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
    "/",
    response_model=NotificationRead,
    dependencies=[Depends(PermissionsDependency([AdminPermission]))],
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
    dependencies=[Depends(PermissionsDependency([AdminPermission]))],
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
    dependencies=[Depends(PermissionsDependency([AdminPermission]))],
)
def delete_notification(*, db_session: Session = Depends(get_db), notification_id: int):
    """
    Delete a notification, returning only an HTTP 200 OK if successful.
    """
    notification = get(db_session=db_session, notification_id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="A notification with this id does not exist.")
    delete(db_session=db_session, notification_id=notification_id)
