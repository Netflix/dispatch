from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.auth.permissions import (
    PermissionsDependency,
    SensitiveProjectActionPermission,
    IndividualContactUpdatePermission,
)
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.exceptions import ExistsError
from dispatch.models import PrimaryKey

from .models import (
    IndividualContactCreate,
    IndividualContactPagination,
    IndividualContactRead,
    IndividualContactUpdate,
)
from .service import get, get_by_email_and_project, create, update, delete


router = APIRouter()


@router.get("/{individual_contact_id}", response_model=IndividualContactRead)
def get_individual(db_session: DbSession, individual_contact_id: PrimaryKey):
    """Gets an individual contact."""
    individual = get(db_session=db_session, individual_contact_id=individual_contact_id)
    if not individual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An individual with this id does not exist."}],
        )
    return individual


@router.get("", response_model=IndividualContactPagination)
def get_individuals(common: CommonParameters):
    """Retrieve individual contacts."""
    return search_filter_sort_paginate(model="IndividualContact", **common)


@router.post("", response_model=IndividualContactRead)
def create_individual(db_session: DbSession, individual_contact_in: IndividualContactCreate):
    """Creates a new individual contact."""
    individual = get_by_email_and_project(
        db_session=db_session,
        email=individual_contact_in.email,
        project_id=individual_contact_in.project.id,
    )
    if individual:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="An individual with this email already exists."),
                    loc="email",
                )
            ],
            model=IndividualContactRead,
        )
    return create(db_session=db_session, individual_contact_in=individual_contact_in)


@router.put(
    "/{individual_contact_id}",
    response_model=IndividualContactRead,
    summary="Updates an individual's contact information.",
    dependencies=[Depends(PermissionsDependency([IndividualContactUpdatePermission]))],
)
def update_individual(
    db_session: DbSession,
    individual_contact_id: PrimaryKey,
    individual_contact_in: IndividualContactUpdate,
):
    """Updates an individual contact."""
    individual = get(db_session=db_session, individual_contact_id=individual_contact_id)
    if not individual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An individual with this id does not exist."}],
        )
    return update(
        db_session=db_session,
        individual_contact=individual,
        individual_contact_in=individual_contact_in,
    )


@router.delete(
    "/{individual_contact_id}",
    response_model=None,
    summary="Deletes an individual contact.",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_individual(db_session: DbSession, individual_contact_id: PrimaryKey):
    """Deletes an individual contact."""
    individual = get(db_session=db_session, individual_contact_id=individual_contact_id)
    if not individual:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An individual with this id does not exist."}],
        )
    delete(db_session=db_session, individual_contact_id=individual_contact_id)
