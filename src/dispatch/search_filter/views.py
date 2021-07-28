from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    SearchFilterCreate,
    SearchFilterUpdate,
    SearchFilterRead,
    SearchFilterPagination,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=SearchFilterPagination)
def get_filters(*, common: dict = Depends(common_parameters)):
    """Retrieve filters."""
    return search_filter_sort_paginate(model="SearchFilter", **common)


@router.post("", response_model=SearchFilterRead)
def create_search_filter(
    *, db_session: Session = Depends(get_db), search_filter_in: SearchFilterCreate
):
    """Create a new filter."""
    try:
        return create(db_session=db_session, search_filter_in=search_filter_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "An search filter with this name already exists.",
                    "loc": ["name"],
                    "type": "Exists",
                }
            ],
        )


@router.put("/{search_filter_id}", response_model=SearchFilterRead)
def update_search_filter(
    *,
    db_session: Session = Depends(get_db),
    search_filter_id: PrimaryKey,
    search_filter_in: SearchFilterUpdate,
):
    """Update a search filter."""
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A search filter with this id does not exist."}],
        )
    try:
        search_filter = update(
            db_session=db_session, search_filter=search_filter, search_filter_in=search_filter_in
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "An search filter with this name already exists.",
                    "loc": ["name"],
                    "type": "Exists",
                }
            ],
        )
    return search_filter


@router.delete("/{search_filter_id}")
def delete_filter(*, db_session: Session = Depends(get_db), search_filter_id: PrimaryKey):
    """Delete a search filter."""
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A search filter with this id does not exist."}],
        )

    delete(db_session=db_session, search_filter_id=search_filter_id)
