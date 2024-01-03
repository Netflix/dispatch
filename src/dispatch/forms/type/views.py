import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import (
    FeedbackDeletePermission,
    PermissionsDependency,
)
from dispatch.auth.service import CurrentUser
from dispatch.database.core import DbSession
from dispatch.database.service import search_filter_sort_paginate, CommonParameters
from dispatch.exceptions import ExistsError
from dispatch.models import PrimaryKey

from .models import FormsTypeRead, FormsTypeCreate, FormsTypeUpdate, FormsTypePagination
from .service import get, delete, create, update

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=FormsTypePagination)
def get_forms(commons: CommonParameters):
    """Get all form types, or only those matching a given search term."""
    return search_filter_sort_paginate(model="FormsType", **commons)


@router.get("/{forms_type_id}", response_model=FormsTypeRead)
def get_form(db_session: DbSession, forms_type_id: PrimaryKey):
    """Get a form type by its id."""
    forms_type = get(db_session=db_session, forms_type_id=forms_type_id)
    if not forms_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form type with this id does not exist."}],
        )
    return forms_type


@router.post("", response_model=FormsTypeRead)
def create_forms_type(
    db_session: DbSession,
    forms_type_in: FormsTypeCreate,
    current_user: CurrentUser,
):
    """Create a new form type."""
    try:
        return create(
            db_session=db_session, creator=current_user, forms_type_in=forms_type_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A form type with this name already exists."), loc="name"
                )
            ],
            model=FormsTypeRead,
        ) from None


@router.put(
    "/{forms_type_id}/{individual_contact_id}",
    response_model=FormsTypeRead,
    dependencies=[Depends(PermissionsDependency([FeedbackDeletePermission]))],
)
def update_forms_type(
    db_session: DbSession,
    forms_type_id: PrimaryKey,
    forms_type_in: FormsTypeUpdate,
):
    """Update a form type."""
    forms_type = get(db_session=db_session, forms_type_id=forms_type_id)
    if not forms_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form type with this id does not exist."}],
        )
    try:
        forms_type = update(
            db_session=db_session, forms_type=forms_type, forms_type_in=forms_type_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A form type with this name already exists."), loc="name"
                )
            ],
            model=FormsTypeUpdate,
        ) from None
    return forms_type

@router.delete(
    "/{forms_type_id}/{individual_contact_id}",
    response_model=None,
    dependencies=[
        Depends(PermissionsDependency([FeedbackDeletePermission]))
    ],
)
def delete_form(db_session: DbSession, forms_type_id: PrimaryKey):
    """Delete a form type, returning only an HTTP 200 OK if successful."""
    forms_type = get(db_session=db_session, forms_type_id=forms_type_id)
    if not forms_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form type with this id does not exist."}],
        )
    delete(db_session=db_session, forms_type_id=forms_type_id)
