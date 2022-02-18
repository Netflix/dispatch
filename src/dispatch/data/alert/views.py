from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.models import PrimaryKey

from .models import (
    AlertCreate,
    AlertRead,
    AlertUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(*, db_session: Session = Depends(get_db), alert_id: PrimaryKey):
    """Given its unique ID, retrieve details about a single alert."""
    alert = get(db_session=db_session, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested alert does not exist."}],
        )
    return alert


@router.post("", response_model=AlertRead)
def create_alert(*, db_session: Session = Depends(get_db), alert_in: AlertCreate):
    """Create a new alert."""
    alert = create(db_session=db_session, alert_in=alert_in)
    return alert


@router.put("/{alert_id}", response_model=AlertRead)
def update_alert(
    *, db_session: Session = Depends(get_db), alert_id: PrimaryKey, alert_in: AlertUpdate
):
    """Update a alert."""
    alert = get(db_session=db_session, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An alert with this ID does not exist."}],
        )
    alert = update(db_session=db_session, alert=alert, alert_in=alert_in)
    return alert


@router.delete("/{alert_id}")
def delete_alert(*, db_session: Session = Depends(get_db), alert_id: PrimaryKey):
    """Delete a alert, returning only an HTTP 200 OK if successful."""
    alert = get(db_session=db_session, alert_id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An alert with this ID does not exist."}],
        )
    delete(db_session=db_session, alert_id=alert_id)
