from fastapi import APIRouter, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    SourceCreate,
    SourcePagination,
    SourceRead,
    SourceUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=SourcePagination)
def get_sources(common: CommonParameters):
    """Get all sources, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Source", **common)


@router.get("/{source_id}", response_model=SourceRead)
def get_source(db_session: DbSession, source_id: PrimaryKey):
    """Given its unique id, retrieve details about a single source."""
    source = get(db_session=db_session, source_id=source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source does not exist."}],
        )
    return source


@router.post("", response_model=SourceRead)
def create_source(db_session: DbSession, source_in: SourceCreate):
    """Creates a new source."""
    return create(db_session=db_session, source_in=source_in)


@router.put("/{source_id}", response_model=SourceRead)
def update_source(db_session: DbSession, source_id: PrimaryKey, source_in: SourceUpdate):
    """Updates a source."""
    source = get(db_session=db_session, source_id=source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source with this id does not exist."}],
        )
    return update(db_session=db_session, source=source, source_in=source_in)


@router.delete("/{source_id}", response_model=None)
def delete_source(db_session: DbSession, source_id: PrimaryKey):
    """Deletes a source, returning only an HTTP 200 OK if successful."""
    source = get(db_session=db_session, source_id=source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source with this id does not exist."}],
        )
    delete(db_session=db_session, source_id=source_id)
