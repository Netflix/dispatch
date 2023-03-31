import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.exc import IntegrityError

from dispatch.auth.service import CurrentUser
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.exceptions import ExistsError
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.project import service as project_service
from dispatch.signal import service as signal_service
from dispatch.signal.flows import signal_instance_create_flow

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
    create_signal_filter,
    delete,
    delete_signal_filter,
    get,
    get_signal_filter,
    update,
    update_signal_filter,
)

router = APIRouter()

log = logging.getLogger(__name__)


@router.get("/instances", response_model=SignalInstancePagination)
def get_signal_instances(*, common: CommonParameters):
    """Get all signal instances."""
    return search_filter_sort_paginate(model="SignalInstance", **common)


@router.post("/instances", response_model=SignalInstanceRead)
def create_signal_instance(
    *,
    db_session: DbSession,
    organization: OrganizationSlug,
    signal_instance_in: SignalInstanceCreate,
    background_tasks: BackgroundTasks,
):
    """Create a new signal instance."""
    project = project_service.get_by_name_or_default(
        db_session=db_session, project_in=signal_instance_in.project
    )

    if not signal_instance_in.signal:
        external_id = signal_instance_in.raw["id"]
        variant = signal_instance_in.raw["variant"]

        signal = signal_service.get_by_variant_or_external_id(
            db_session=db_session,
            project_id=project.id,
            external_id=external_id,
            variant=variant,
        )

        signal_instance_in.signal = signal

    if not signal:
        msg = f"No signal definition found. Id: {external_id} Variant: {variant}"
        log.error(msg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": msg}],
        ) from None

    if not signal.enabled:
        msg = f"Signal definition not enabled. SignalName: {signal.name}"
        log.warning(msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": msg}],
        ) from None

    signal_instance = signal_service.create_instance(
        db_session=db_session, signal_instance_in=signal_instance_in
    )
    signal_instance.signal = signal
    db_session.commit()

    background_tasks.add_task(
        signal_instance_create_flow, signal_instance.id, organization_slug=organization
    )

    return signal_instance


@router.get("/filters", response_model=SignalFilterPagination)
def get_signal_filters(*, common: CommonParameters):
    """Get all signal filters."""
    return search_filter_sort_paginate(model="SignalFilter", **common)


@router.post("/filters", response_model=SignalFilterRead)
def create_filter(
    *,
    db_session: DbSession,
    signal_filter_in: SignalFilterCreate,
    current_user: CurrentUser,
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
    db_session: DbSession,
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
def delete_filter(*, db_session: DbSession, signal_filter_id: PrimaryKey):
    """Deletes a signal filter."""
    signal_filter = get(db_session=db_session, signal_filter_id=signal_filter_id)
    if not signal_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal filter with this id does not exist."}],
        )
    delete_signal_filter(db_session=db_session, signal_filter_id=signal_filter_id)


@router.get("", response_model=SignalPagination)
def get_signals(*, common: CommonParameters):
    """Get all signal definitions."""
    return search_filter_sort_paginate(model="Signal", **common)


@router.get("/{signal_id}", response_model=SignalRead)
def get_signal(*, db_session: DbSession, signal_id: PrimaryKey):
    """Get a signal by it's ID."""
    signal = get(db_session=db_session, signal_id=signal_id)
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal with this id does not exist."}],
        )
    return signal


@router.post("", response_model=SignalRead)
def create_signal(*, db_session: DbSession, signal_in: SignalCreate):
    """Create a new signal."""
    return create(db_session=db_session, signal_in=signal_in)


@router.put("/{signal_id}", response_model=SignalRead)
def update_signal(*, db_session: DbSession, signal_id: PrimaryKey, signal_in: SignalUpdate):
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
def delete_signal(*, db_session: DbSession, signal_id: PrimaryKey):
    """Deletes a signal."""
    signal = get(db_session=db_session, signal_id=signal_id)
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal with this id does not exist."}],
        )
    delete(db_session=db_session, signal_id=signal_id)
