from fastapi import APIRouter, HTTPException, status, Depends

from dispatch.auth.permissions import (
    FeedbackDeletePermission,
    PermissionsDependency,
)
from dispatch.database.core import DbSession
from dispatch.database.service import search_filter_sort_paginate, CommonParameters
from dispatch.models import PrimaryKey

from .models import FormsRead, FormsPagination
from .service import get, delete


router = APIRouter()


@router.get("", response_model=FormsPagination)
def get_forms(commons: CommonParameters):
    """Get all forms, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Forms", **commons)


@router.get("/{form_id}", response_model=FormsRead)
def get_form(db_session: DbSession, form_id: PrimaryKey):
    """Get a form by its id."""
    form = get(db_session=db_session, form_id=form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form with this id does not exist."}],
        )
    return form


# here the individual_contact_id is the creator of the form
# used to validate if they have permission to delete
@router.delete(
    "/{form_id}/{individual_contact_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([FeedbackDeletePermission]))],
)
def delete_form(db_session: DbSession, form_id: PrimaryKey):
    """Delete a form, returning only an HTTP 200 OK if successful."""
    form = get(db_session=db_session, form_id=form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form with this id does not exist."}],
        )
    delete(db_session=db_session, form_id=form_id)
