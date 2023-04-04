from fastapi import APIRouter, HTTPException, status


from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
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
def get_source_transports(common: CommonParameters):
    """Get all source transports, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceTransport", **common)


@router.get("/{source_transport_id}", response_model=SourceTransportRead)
def get_source_transport(db_session: DbSession, source_transport_id: PrimaryKey):
    """Given its unique id, retrieve details about a single source transport."""
    transport = get(db_session=db_session, source_transport_id=source_transport_id)
    if not transport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source transport does not exist."}],
        )
    return transport


@router.post("", response_model=SourceTransportRead)
def create_source_transport(db_session: DbSession, source_transport_in: SourceTransportCreate):
    """Creates a new source transport."""
    return create(db_session=db_session, source_transport_in=source_transport_in)


@router.put("/{source_transport_id}", response_model=SourceTransportRead)
def update_source_transport(
    db_session: DbSession,
    source_transport_id: PrimaryKey,
    source_transport_in: SourceTransportUpdate,
):
    """Updates a source transport."""
    transport = get(db_session=db_session, source_transport_id=source_transport_id)
    if not transport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source transport with this id does not exist."}],
        )
    return update(
        db_session=db_session, source_transport=transport, source_transport_in=source_transport_in
    )


@router.delete("/{source_transport_id}", response_model=None)
def delete_source_transport(db_session: DbSession, source_transport_id: PrimaryKey):
    """Deletes a source transport, returning only an HTTP 200 OK if successful."""
    transport = get(db_session=db_session, source_transport_id=source_transport_id)
    if not transport:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source transport with this id does not exist."}],
        )
    delete(db_session=db_session, source_transport_id=source_transport_id)
