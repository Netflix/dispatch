from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    SourceStatusCreate,
    SourceStatusPagination,
    SourceStatusRead,
    SourceStatusUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=SourceStatusPagination)
def get_source_statuses(*, common: dict = Depends(common_parameters)):
    """Get all source statuses, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceStatus", **common)


@router.get("/{source_status_id}", response_model=SourceStatusRead)
def get_source_status(*, db_session: Session = Depends(get_db), source_status_id: PrimaryKey):
    """Given its unique ID, retrieve details about a single source status."""
    status = get(db_session=db_session, source_status_id=source_status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source status does not exist."}],
        )
    return status


@router.post("", response_model=SourceStatusRead)
def create_source_status(
    *, db_session: Session = Depends(get_db), source_status_in: SourceStatusCreate
):
    """Create a new source status."""
    return create(db_session=db_session, source_status_in=source_status_in)


@router.put("/{source_status_id}", response_model=SourceStatusRead)
def update_source_status(
    *,
    db_session: Session = Depends(get_db),
    source_status_id: PrimaryKey,
    source_status_in: SourceStatusUpdate,
):
    """Update a status status."""
    status = get(db_session=db_session, source_status_id=source_status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source status with this ID does not exist."}],
        )
    status = update(db_session=db_session, source_status=status, source_status_in=source_status_in)
    return status


@router.delete("/{source_status_id}")
def delete_source_status(*, db_session: Session = Depends(get_db), source_status_id: PrimaryKey):
    """Delete a source status, returning only an HTTP 200 OK if successful."""
    status = get(db_session=db_session, source_status_id=source_status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source status with this ID does not exist."}],
        )
    delete(db_session=db_session, source_status_id=source_status_id)
