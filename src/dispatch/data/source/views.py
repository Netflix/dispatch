from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
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
def get_sources(*, common: dict = Depends(common_parameters)):
    """Get all sources, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Source", **common)


@router.get("/{source_id}", response_model=SourceRead)
def get_source(*, db_session: Session = Depends(get_db), source_id: PrimaryKey):
    """Given its unique ID, retrieve details about a single source."""
    source = get(db_session=db_session, source_id=source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source does not exist."}],
        )
    return source


@router.post("", response_model=SourceRead)
def create_source(*, db_session: Session = Depends(get_db), source_in: SourceCreate):
    """Create a new source."""
    source = create(db_session=db_session, source_in=source_in)
    return source


@router.put("/{source_id}", response_model=SourceRead)
def update_source(
    *, db_session: Session = Depends(get_db), source_id: PrimaryKey, source_in: SourceUpdate
):
    """Update a source."""
    source = get(db_session=db_session, source_id=source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source with this ID does not exist."}],
        )
    source = update(db_session=db_session, source=source, source_in=source_in)
    return source


@router.delete("/{source_id}")
def delete_source(*, db_session: Session = Depends(get_db), source_id: PrimaryKey):
    """Delete a source, returning only an HTTP 200 OK if successful."""
    source = get(db_session=db_session, source_id=source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source with this ID does not exist."}],
        )
    delete(db_session=db_session, source_id=source_id)
