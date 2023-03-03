from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.exceptions import ExistsError
from dispatch.models import PrimaryKey

from .models import (
    SignalCreate,
    SignalFilterCreate,
    SignalFilterPagination,
    SignalFilterRead,
    SignalFilterUpdate,
    SignalInstanceCreate,
    SignalInstancePagination,
    SignalInstanceRead,
    SignalPagination,
    SignalRead,
    SignalUpdate,
)
from .service import (
    create,
    create_instance,
    create_signal_filter,
    delete,
    delete_signal_filter,
    get,
    get_signal_filter,
    update,
    update_signal_filter,
)

router = APIRouter()


@router.get("/instances", response_model=SignalInstancePagination)
def get_signal_instances(*, common: dict = Depends(common_parameters)):
    """Get all signal instances."""
    return search_filter_sort_paginate(model="SignalInstance", **common)


@router.post("/{signal_id}/instances", response_model=SignalInstanceRead)
def create_signal_instance(
    *, db_session: Session = Depends(get_db), signal_instance_in: SignalInstanceCreate
):
    """Create a new signal instance."""
    return create_instance(db_session=db_session, signal_instance_in=signal_instance_in)


@router.get("/filters", response_model=SignalFilterPagination)
def get_signal_filters(*, common: dict = Depends(common_parameters)):
    """Get all signal filters."""
    return search_filter_sort_paginate(model="SignalFilter", **common)


@router.post("/filters", response_model=SignalFilterRead)
def create_filter(
    *,
    db_session: Session = Depends(get_db),
    signal_filter_in: SignalFilterCreate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """Create a new signal filter."""
    try:
        return create_signal_filter(
            db_session=db_session, creator=current_user, signal_filter_in=signal_filter_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A signal filter with this name already exists."), loc="name"
                )
            ],
            model=SignalFilterRead,
        ) from None


@router.put("/filters/{signal_filter_id}", response_model=SignalRead)
def update_filter(
    *,
    db_session: Session = Depends(get_db),
    signal_filter_id: PrimaryKey,
    signal_filter_in: SignalFilterUpdate,
):
    """Updates an existing signal filter."""
    signal_filter = get_signal_filter(db_session=db_session, signal_id=signal_filter_id)
    if not signal_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal filter with this id does not exist."}],
        )

    try:
        signal_filter = update_signal_filter(
            db_session=db_session, signal_filter=signal_filter, signal_filter_in=signal_filter_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A signal filter with this name already exists."), loc="name"
                )
            ],
            model=SignalFilterUpdate,
        ) from None

    return signal_filter


@router.delete("/filters/{signal_filter_id}", response_model=None)
def delete_filter(*, db_session: Session = Depends(get_db), signal_filter_id: PrimaryKey):
    """Deletes a signal filter."""
    signal_filter = get(db_session=db_session, signal_filter_id=signal_filter_id)
    if not signal_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal filter with this id does not exist."}],
        )
    delete_signal_filter(db_session=db_session, signal_filter_id=signal_filter_id)


@router.get("", response_model=SignalPagination)
def get_signals(*, common: dict = Depends(common_parameters)):
    """Get all signal definitions."""
    return search_filter_sort_paginate(model="Signal", **common)


@router.get("/{signal_id}", response_model=SignalRead)
def get_signal(*, db_session: Session = Depends(get_db), signal_id: PrimaryKey):
    """Get a signal by it's ID."""
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


@router.put("/{signal_id}", response_model=SignalRead)
def update_signal(
    *, db_session: Session = Depends(get_db), signal_id: PrimaryKey, signal_in: SignalUpdate
):
    """Updates an existing signal."""
    signal = get(db_session=db_session, signal_id=signal_id)
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal with this id does not exist."}],
        )

    try:
        signal = update(db_session=db_session, signal=signal, signal_in=signal_in)
    except IntegrityError:
        raise ValidationError(
            [ErrorWrapper(ExistsError(msg="A signal with this name already exists."), loc="name")],
            model=SignalUpdate,
        ) from None

    return signal


@router.delete("/{signal_id}", response_model=None)
def delete_signal(*, db_session: Session = Depends(get_db), signal_id: PrimaryKey):
    """Deletes a signal."""
    signal = get(db_session=db_session, signal_id=signal_id)
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal with this id does not exist."}],
        )
    delete(db_session=db_session, signal_id=signal_id)
