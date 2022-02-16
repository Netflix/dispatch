from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    SourceTransportCreate,
    SourceTransportPagination,
    SourceTransportRead,
    SourceTransportUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=SourceTransportPagination)
def get_source_transports(*, common: dict = Depends(common_parameters)):
    """Get all source transports, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Sourcetransport", **common)


@router.get("/{source_transport_id}", response_model=SourceTransportRead)
def get_source_transport(*, db_session: Session = Depends(get_db), source_transport_id: PrimaryKey):
    """Given its unique ID, retrieve details about a single source transport."""
    source = get(db_session=db_session, source_transport_id=source_transport_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source transport does not exist."}],
        )
    return source


@router.post("", response_model=SourceTransportRead)
def create_source_transport(
    *, db_session: Session = Depends(get_db), source_transport_in: SourceTransportCreate
):
    """Create a new source transport."""
    source = create(db_session=db_session, source_transport_in=source_transport_in)
    return source


@router.put("/{source_transport_id}", response_model=SourceTransportRead)
def update_source_transport(
    *,
    db_session: Session = Depends(get_db),
    source_transport_id: PrimaryKey,
    source_transport_in: SourceTransportUpdate,
):
    """Update a source transport."""
    source = get(db_session=db_session, source_transport_id=source_transport_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source transport with this ID does not exist."}],
        )
    source = update(db_session=db_session, source=source, source_transport_in=source_transport_in)
    return source


@router.delete("/{source_transport_id}")
def delete_source_transport(
    *, db_session: Session = Depends(get_db), source_transport_id: PrimaryKey
):
    """Delete a source transport, returning only an HTTP 200 OK if successful."""
    source = get(db_session=db_session, source_transport_id=source_transport_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source transport with this ID does not exist."}],
        )
    delete(db_session=db_session, source_transport_id=source_transport_id)
