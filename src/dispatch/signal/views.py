from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    SignalCreate,
    SignalPagination,
    SignalRead,
    SignalInstanceRead,
    SignalInstanceCreate,
)
from .service import create, get, create_instance

router = APIRouter()


@router.get("", response_model=SignalPagination)
def get_signals(*, common: dict = Depends(common_parameters)):
    """Get all signal definitions."""
    return search_filter_sort_paginate(model="Signal", **common)


@router.get("/{signal_id}", response_model=SignalRead)
def get_signal(*, db_session: Session = Depends(get_db), signal_id: PrimaryKey):
    """Update a signal."""
    signal = get(db_session=db_session, signal_id=signal_id)
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal with this id does not exist."}],
        )
    return signal


@router.post("", response_model=SignalRead)
def create_signal(*, db_session: Session = Depends(get_db), signal_in: SignalCreate):
    """Create a new signal."""
    return create(db_session=db_session, signal_in=signal_in)


@router.post("/{signal_id}/instances", response_model=SignalInstanceRead)
def create_signal_instance(
    *, db_session: Session = Depends(get_db), signal_instance_in: SignalInstanceCreate
):
    """Create a new signal instance."""
    return create_instance(db_session=db_session, signal_instance_in=signal_instance_in)
