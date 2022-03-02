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
    """Get all source_data_format data formats, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceDataFormat", **common)


@router.get("/{source_data_format_id}", response_model=SourceDataFormatRead)
def get_source_data_format(
    *, db_session: Session = Depends(get_db), source_data_format_id: PrimaryKey
):
    """Given its unique ID, retrieve details about a data format."""
    source_data_format = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source_data_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested data format does not exist."}],
        )
    return source_data_format


@router.post("", response_model=SourceDataFormatRead)
def create_source_data_format(
    *, db_session: Session = Depends(get_db), source_data_format_in: SourceDataFormatCreate
):
    """Create a new data format."""
    source_data_format = create(db_session=db_session, source_data_format_in=source_data_format_in)
    return source_data_format


@router.put("/{source_data_format_id}", response_model=SourceDataFormatRead)
def update_source_data_format(
    *,
    db_session: Session = Depends(get_db),
    source_data_format_id: PrimaryKey,
    source_data_format_in: SourceDataFormatUpdate,
):
    """Update a data format."""
    source_data_format = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source_data_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An data format with this ID does not exist."}],
        )
    source_data_format = update(
        db_session=db_session,
        source_data_format=source_data_format,
        source_data_format_in=source_data_format_in,
    )
    return source_data_format


@router.delete("/{source_data_format_id}")
def delete_source_data_format(
    *, db_session: Session = Depends(get_db), source_data_format_id: PrimaryKey
):
    """Delete a data format, returning only an HTTP 200 OK if successful."""
    source_data_format = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source_data_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An data format with this ID does not exist."}],
        )
    delete(db_session=db_session, source_data_format_id=source_data_format_id)
