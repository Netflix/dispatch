from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

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
    """
    Retrieve filters.
    """
    return search_filter_sort_paginate(model="SearchFilter", **common)


@router.post("", response_model=SearchFilterRead)
def create_search_filter(
    *, db_session: Session = Depends(get_db), search_filter_in: SearchFilterCreate
):
    """
    Create a new filter.
    """
    try:
        search_filter = create(db_session=db_session, search_filter_in=search_filter_in)
        return search_filter
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="A search filter already exists with this name."
        )


@router.put("/{search_filter_id}", response_model=SearchFilterRead)
def update_search_filter(
    *,
    db_session: Session = Depends(get_db),
    search_filter_id: int,
    search_filter_in: SearchFilterUpdate,
):
    """
    Update a search filter.
    """
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(status_code=404, detail="A search_filter with this id does not exist.")
    search_filter = update(
        db_session=db_session, search_filter=search_filter, search_filter_in=search_filter_in
    )
    return search_filter


@router.delete("/{search_filter_id}")
def delete_filter(*, db_session: Session = Depends(get_db), search_filter_id: int):
    """
    Delete a search filter.
    """
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(status_code=404, detail="A search_filter with this id does not exist.")

    delete(db_session=db_session, search_filter_id=search_filter_id)
