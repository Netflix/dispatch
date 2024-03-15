import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import (
    SensitiveProjectActionPermission,
    PermissionsDependency,
)
from dispatch.database.core import DbSession
from dispatch.auth.service import CurrentUser
from dispatch.database.service import search_filter_sort_paginate, CommonParameters
from dispatch.models import PrimaryKey
from dispatch.exceptions import ExistsError

from .models import EmailTemplatesRead, EmailTemplatesUpdate, EmailTemplatesPagination, EmailTemplatesCreate
from .service import get, create, update, delete

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=EmailTemplatesPagination)
def get_email_templates(commons: CommonParameters):
    """Get all email templates, or only those matching a given search term."""
    return search_filter_sort_paginate(model="EmailTemplates", **commons)


@router.get("/{email_template_id}", response_model=EmailTemplatesRead)
def get_email_template(db_session: DbSession, email_template_id: PrimaryKey):
    """Get an email template by its id."""
    email_template = get(db_session=db_session, email_template_id=email_template_id)
    if not email_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An email template with this id does not exist."}],
        )
    return email_template


@router.post("", response_model=EmailTemplatesRead)
def create_email_template(
    db_session: DbSession,
    email_template_in: EmailTemplatesCreate,
    current_user: CurrentUser,
):
    """Create a new email template."""
    try:
        return create(
            db_session=db_session, email_template_in=email_template_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="An email template with this type already exists."), loc="name"
                )
            ],
            model=EmailTemplatesRead,
        ) from None


@router.put(
    "/{email_template_id}",
    response_model=EmailTemplatesRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_email_template(
    db_session: DbSession,
    email_template_id: PrimaryKey,
    email_template_in: EmailTemplatesUpdate,
):
    """Update a search filter."""
    email_template = get(db_session=db_session, email_template_id=email_template_id)
    if not email_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An email template with this id does not exist."}],
        )
    try:
        email_template = update(
            db_session=db_session, email_template=email_template, email_template_in=email_template_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="An email template with this type already exists."), loc="name"
                )
            ],
            model=EmailTemplatesUpdate,
        ) from None
    return email_template


@router.delete(
    "/{email_template_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_email_template(db_session: DbSession, email_template_id: PrimaryKey):
    """Delete an email template, returning only an HTTP 200 OK if successful."""
    email_template = get(db_session=db_session, email_template_id=email_template_id)
    if not email_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An email template with this id does not exist."}],
        )
    delete(db_session=db_session, email_template_id=email_template_id)
