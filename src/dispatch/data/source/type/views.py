from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
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
def get_source_types(*, common: dict = Depends(common_parameters)):
    """Get all source types, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceType", **common)


@router.get("/{source_type_id}", response_model=SourceTypeRead)
def get_source_type(*, db_session: Session = Depends(get_db), source_type_id: PrimaryKey):
    """Given its unique ID, retrieve details about a single source type."""
    source_type = get(db_session=db_session, source_type_id=source_type_id)
    if not source_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source type does not exist."}],
        )
    return source_type


@router.post("", response_model=SourceTypeRead)
def create_source_type(*, db_session: Session = Depends(get_db), source_type_in: SourceTypeCreate):
    """Create a new source type."""
    return create(db_session=db_session, source_type_in=source_type_in)


@router.put("/{source_type_id}", response_model=SourceTypeRead)
def update_source_type(
    *,
    db_session: Session = Depends(get_db),
    source_type_id: PrimaryKey,
    source_type_in: SourceTypeUpdate,
):
    """Update a source type."""
    source_type = get(db_session=db_session, source_type_id=source_type_id)
    if not source_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source type with this ID does not exist."}],
        )
    return update(db_session=db_session, source_type=source_type, source_type_in=source_type_in)


@router.delete("/{source_type_id}")
def delete_source_type(*, db_session: Session = Depends(get_db), source_type_id: PrimaryKey):
    """Delete a source type, returning only an HTTP 200 OK if successful."""
    source_type = get(db_session=db_session, source_type_id=source_type_id)
    if not source_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source type with this ID does not exist."}],
        )
    delete(db_session=db_session, source_type_id=source_type_id)
