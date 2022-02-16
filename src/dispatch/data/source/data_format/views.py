from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    SourceDataFormatCreate,
    SourceDataFormatPagination,
    SourceDataFormatRead,
    SourceDataFormatUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=SourceDataFormatPagination)
def get_source_data_formats(*, common: dict = Depends(common_parameters)):
    """Get all source data formats, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceDataFormat", **common)


@router.get("/{source_data_format_id}", response_model=SourceDataFormatRead)
def get_source_data_format(
    *, db_session: Session = Depends(get_db), source_data_format_id: PrimaryKey
):
    """Given its unique ID, retrieve details about a single source data format."""
    source = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source data format does not exist."}],
        )
    return source


@router.post("", response_model=SourceDataFormatRead)
def create_source_data_format(
    *, db_session: Session = Depends(get_db), source_data_format_in: SourceDataFormatCreate
):
    """Create a new source data format."""
    source = create(db_session=db_session, source_data_format_in=source_data_format_in)
    return source


@router.put("/{source_data_format_id}", response_model=SourceDataFormatRead)
def update_source_data_format(
    *,
    db_session: Session = Depends(get_db),
    source_data_format_id: PrimaryKey,
    source_data_format_in: SourceDataFormatUpdate,
):
    """Update a source data_format."""
    source = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source data format with this ID does not exist."}],
        )
    source = update(
        db_session=db_session, source=source, source_data_format_in=source_data_format_in
    )
    return source


@router.delete("/{source_data_format_id}")
def delete_source_data_format(
    *, db_session: Session = Depends(get_db), source_data_format_id: PrimaryKey
):
    """Delete a source data format, returning only an HTTP 200 OK if successful."""
    source = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source data format with this ID does not exist."}],
        )
    delete(db_session=db_session, source_data_format_id=source_data_format_id)
