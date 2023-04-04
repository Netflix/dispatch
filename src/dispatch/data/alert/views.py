from fastapi import APIRouter, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.models import PrimaryKey

from .models import (
    AlertCreate,
    AlertRead,
    AlertUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(db_session: DbSession, alert_id: PrimaryKey):
    """Given its unique id, retrieve details about a single alert."""
    alert = get(db_session=db_session, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested alert does not exist."}],
        )
    return alert


@router.post("", response_model=AlertRead)
def create_alert(db_session: DbSession, alert_in: AlertCreate):
    """Creates a new alert."""
    return create(db_session=db_session, alert_in=alert_in)


@router.put("/{alert_id}", response_model=AlertRead)
def update_alert(db_session: DbSession, alert_id: PrimaryKey, alert_in: AlertUpdate):
    """Updates an alert."""
    alert = get(db_session=db_session, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An alert with this id does not exist."}],
        )
    return update(db_session=db_session, alert=alert, alert_in=alert_in)


@router.delete("/{alert_id}", response_model=None)
def delete_alert(db_session: DbSession, alert_id: PrimaryKey):
    """Deletes an alert, returning only an HTTP 200 OK if successful."""
    alert = get(db_session=db_session, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An alert with this id does not exist."}],
        )
    delete(db_session=db_session, alert_id=alert_id)
