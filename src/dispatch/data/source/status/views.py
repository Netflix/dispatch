from fastapi import APIRouter, HTTPException


from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
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
def get_source_statuses(common: CommonParameters):
    """Get all source statuses, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceStatus", **common)


@router.get("/{source_status_id}", response_model=SourceStatusRead)
def get_source_status(db_session: DbSession, source_status_id: PrimaryKey):
    """Given its unique id, retrieve details about a single source status."""
    status = get(db_session=db_session, source_status_id=source_status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source status does not exist."}],
        )
    return status


@router.post("", response_model=SourceStatusRead)
def create_source_status(db_session: DbSession, source_status_in: SourceStatusCreate):
    """Creates a new source status."""
    return create(db_session=db_session, source_status_in=source_status_in)


@router.put("/{source_status_id}", response_model=SourceStatusRead)
def update_source_status(
    db_session: DbSession,
    source_status_id: PrimaryKey,
    source_status_in: SourceStatusUpdate,
):
    """Updates a source status."""
    status = get(db_session=db_session, source_status_id=source_status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source status with this id does not exist."}],
        )
    return update(db_session=db_session, source_status=status, source_status_in=source_status_in)


@router.delete("/{source_status_id}", response_model=None)
def delete_source_status(db_session: DbSession, source_status_id: PrimaryKey):
    """Deletes a source status, returning only an HTTP 200 OK if successful."""
    status = get(db_session=db_session, source_status_id=source_status_id)
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source status with this id does not exist."}],
        )
    delete(db_session=db_session, source_status_id=source_status_id)
