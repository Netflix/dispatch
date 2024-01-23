import logging
from fastapi import APIRouter, HTTPException, status, Depends, Response
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import (
    FeedbackDeletePermission,
    PermissionsDependency,
)
from dispatch.database.core import DbSession
from dispatch.auth.service import CurrentUser
from dispatch.database.service import search_filter_sort_paginate, CommonParameters
from dispatch.models import PrimaryKey
from dispatch.exceptions import ExistsError
from dispatch.forms.type.service import send_email_to_service

from .models import FormsRead, FormsUpdate, FormsPagination
from .service import get, create, update, delete

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=FormsPagination)
def get_forms(commons: CommonParameters):
    """Get all forms, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Forms", **commons)


@router.get("/{form_id}", response_model=FormsRead)
def get_form(db_session: DbSession, form_id: PrimaryKey):
    """Get a form by its id."""
    form = get(db_session=db_session, forms_id=form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form with this id does not exist."}],
        )
    return form


@router.post("/completed/{form_id}", response_model=FormsRead)
def sendEmailToService(db_session: DbSession, form_id: PrimaryKey):
    """Sends an email to service indicating form is complete"""
    form = get(db_session=db_session, forms_id=form_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form with this id does not exist."}],
        )
    if not form.form_type or not form.form_type.service:
        log.warning(f"Missing form type or form type service for form: {form}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    send_email_to_service(db_session=db_session, service=form.form_type.service, form=form)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("", response_model=FormsRead)
def create_forms(
    db_session: DbSession,
    forms_in: dict,
    current_user: CurrentUser,
):
    """Create a new form."""
    try:
        return create(
            db_session=db_session, creator=current_user, forms_in=forms_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A search filter with this name already exists."), loc="name"
                )
            ],
            model=FormsRead,
        ) from None


@router.put(
    "/{forms_id}/{individual_contact_id}",
    response_model=FormsRead,
    dependencies=[Depends(PermissionsDependency([FeedbackDeletePermission]))],
)
def update_forms(
    db_session: DbSession,
    forms_id: PrimaryKey,
    forms_in: FormsUpdate,
):
    """Update a search filter."""
    forms = get(db_session=db_session, forms_id=forms_id)
    if not forms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form with this id does not exist."}],
        )
    try:
        forms = update(
            db_session=db_session, forms=forms, forms_in=forms_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A form with this name already exists."), loc="name"
                )
            ],
            model=FormsUpdate,
        ) from None
    return forms


# here the individual_contact_id is the creator of the form
# used to validate if they have permission to delete
@router.delete(
    "/{forms_id}/{individual_contact_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([FeedbackDeletePermission]))],
)
def delete_form(db_session: DbSession, forms_id: PrimaryKey):
    """Delete a form, returning only an HTTP 200 OK if successful."""
    form = get(db_session=db_session, forms_id=forms_id)
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form with this id does not exist."}],
        )
    delete(db_session=db_session, forms_id=forms_id)
