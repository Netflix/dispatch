from fastapi import APIRouter, HTTPException, status, Depends
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import PermissionsDependency
from dispatch.auth.service import CurrentUser
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.exceptions import ExistsError
from dispatch.models import PrimaryKey

from .models import (
    SearchFilterCreate,
    SearchFilterPagination,
    SearchFilterRead,
    SearchFilterUpdate,
)
from .permissions import SearchFilterEditDeletePermission
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=SearchFilterPagination)
def get_filters(common: CommonParameters):
    """Retrieve filters."""
    return search_filter_sort_paginate(model="SearchFilter", **common)


@router.post("", response_model=SearchFilterRead)
def create_search_filter(
    db_session: DbSession,
    search_filter_in: SearchFilterCreate,
    current_user: CurrentUser,
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
        ) from None


@router.put(
    "/{search_filter_id}",
    response_model=SearchFilterRead,
    dependencies=[Depends(PermissionsDependency([SearchFilterEditDeletePermission]))],
)
def update_search_filter(
    db_session: DbSession,
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
        ) from None
    return search_filter


@router.delete(
    "/{search_filter_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([SearchFilterEditDeletePermission]))],
)
def delete_filter(db_session: DbSession, search_filter_id: PrimaryKey):
    """Delete a search filter."""
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A search filter with this id does not exist."}],
        )
    delete(db_session=db_session, search_filter_id=search_filter_id)
