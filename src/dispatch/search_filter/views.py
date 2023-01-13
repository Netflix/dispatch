from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.exceptions import ExistsError
from dispatch.models import PrimaryKey
from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user

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
    *,
    db_session: Session = Depends(get_db),
    search_filter_in: SearchFilterCreate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """Create a new filter."""
    try:
        return create(
            db_session=db_session, creator=current_user, search_filter_in=search_filter_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A search filter with this name already exists."), loc="name"
                )
            ],
            model=SearchFilterRead,
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
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A search filter with this name already exists."), loc="name"
                )
            ],
            model=SearchFilterUpdate,
        )
    return search_filter


@router.delete("/{search_filter_id}", response_model=None)
def delete_filter(*, db_session: Session = Depends(get_db), search_filter_id: PrimaryKey):
    """Delete a search filter."""
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A search filter with this id does not exist."}],
        )
    delete(db_session=db_session, search_filter_id=search_filter_id)
