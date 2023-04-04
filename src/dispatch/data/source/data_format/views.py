from fastapi import APIRouter, HTTPException, status


from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
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
def get_source_data_formats(common: CommonParameters):
    """Get all source data formats, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceDataFormat", **common)


@router.get("/{source_data_format_id}", response_model=SourceDataFormatRead)
def get_source_data_format(db_session: DbSession, source_data_format_id: PrimaryKey):
    """Given its unique id, retrieve details about a source data format."""
    source_data_format = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source_data_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested data format does not exist."}],
        )
    return source_data_format


@router.post("", response_model=SourceDataFormatRead)
def create_source_data_format(db_session: DbSession, source_data_format_in: SourceDataFormatCreate):
    """Creates a new source data format."""
    return create(db_session=db_session, source_data_format_in=source_data_format_in)


@router.put("/{source_data_format_id}", response_model=SourceDataFormatRead)
def update_source_data_format(
    db_session: DbSession,
    source_data_format_id: PrimaryKey,
    source_data_format_in: SourceDataFormatUpdate,
):
    """Updates a source data format."""
    source_data_format = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source_data_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source data format with this id does not exist."}],
        )
    return update(
        db_session=db_session,
        source_data_format=source_data_format,
        source_data_format_in=source_data_format_in,
    )


@router.delete("/{source_data_format_id}", response_model=None)
def delete_source_data_format(db_session: DbSession, source_data_format_id: PrimaryKey):
    """Delete a source data format, returning only an HTTP 200 OK if successful."""
    source_data_format = get(db_session=db_session, source_data_format_id=source_data_format_id)
    if not source_data_format:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source data format with this id does not exist."}],
        )
    delete(db_session=db_session, source_data_format_id=source_data_format_id)
