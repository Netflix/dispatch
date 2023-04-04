from fastapi import APIRouter, HTTPException, status


from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    SourceTypeCreate,
    SourceTypePagination,
    SourceTypeRead,
    SourceTypeUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=SourceTypePagination)
def get_source_types(common: CommonParameters):
    """Get all source types, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceType", **common)


@router.get("/{source_type_id}", response_model=SourceTypeRead)
def get_source_type(db_session: DbSession, source_type_id: PrimaryKey):
    """Given its unique id, retrieve details about a single source type."""
    source_type = get(db_session=db_session, source_type_id=source_type_id)
    if not source_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source type does not exist."}],
        )
    return source_type


@router.post("", response_model=SourceTypeRead)
def create_source_type(db_session: DbSession, source_type_in: SourceTypeCreate):
    """Creates a new source type."""
    return create(db_session=db_session, source_type_in=source_type_in)


@router.put("/{source_type_id}", response_model=SourceTypeRead)
def update_source_type(
    db_session: DbSession,
    source_type_id: PrimaryKey,
    source_type_in: SourceTypeUpdate,
):
    """Updates a source type."""
    source_type = get(db_session=db_session, source_type_id=source_type_id)
    if not source_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source type with this id does not exist."}],
        )
    return update(db_session=db_session, source_type=source_type, source_type_in=source_type_in)


@router.delete("/{source_type_id}", response_model=None)
def delete_source_type(db_session: DbSession, source_type_id: PrimaryKey):
    """Deletes a source type, returning only an HTTP 200 OK if successful."""
    source_type = get(db_session=db_session, source_type_id=source_type_id)
    if not source_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source type with this id does not exist."}],
        )
    delete(db_session=db_session, source_type_id=source_type_id)
