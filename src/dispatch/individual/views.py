from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.auth.permissions import PermissionsDependency, SensitiveProjectActionPermission

from .models import (
    IndividualContactCreate,
    IndividualContactPagination,
    IndividualContactRead,
    IndividualContactUpdate,
)
from .service import create, delete, get, get_by_email, update

router = APIRouter()


@router.get("", response_model=IndividualContactPagination)
def get_individuals(*, common: dict = Depends(common_parameters)):
    """
    Retrieve individual contacts.
    """
    return search_filter_sort_paginate(model="IndividualContact", **common)


@router.post("", response_model=IndividualContactRead)
def create_individual(
    *, db_session: Session = Depends(get_db), individual_contact_in: IndividualContactCreate
):
    """
    Create a new individual contact.
    """
    individual = get_by_email(db_session=db_session, email=individual_contact_in.email)
    if individual:
        raise HTTPException(
            status_code=400, detail="The individual with this email already exists."
        )
    individual = create(db_session=db_session, individual_contact_in=individual_contact_in)
    return individual


@router.get("/{individual_contact_id}", response_model=IndividualContactRead)
def get_individual(*, db_session: Session = Depends(get_db), individual_contact_id: int):
    """
    Get a individual contact.
    """
    individual = get(db_session=db_session, individual_contact_id=individual_contact_id)
    if not individual:
        raise HTTPException(status_code=404, detail="The individual with this id does not exist.")
    return individual


@router.put(
    "/{individual_contact_id}",
    response_model=IndividualContactRead,
    summary="Update an individuals contact information.",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_individual(
    *,
    db_session: Session = Depends(get_db),
    individual_contact_id: int,
    individual_contact_in: IndividualContactUpdate,
):
    """
    Update a individual contact.
    """
    individual = get(db_session=db_session, individual_contact_id=individual_contact_id)
    if not individual:
        raise HTTPException(status_code=404, detail="The individual with this id does not exist.")
    individual = update(
        db_session=db_session,
        individual_contact=individual,
        individual_contact_in=individual_contact_in,
    )
    return individual


@router.delete(
    "/{individual_contact_id}",
    summary="Delete an individual contact.",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
async def delete_individual(*, db_session: Session = Depends(get_db), individual_contact_id: int):
    """
    Delete a individual contact.
    """
    individual = get(db_session=db_session, individual_contact_id=individual_contact_id)
    if not individual:
        raise HTTPException(status_code=404, detail="The individual with this id does not exist.")

    delete(db_session=db_session, individual_contact_id=individual_contact_id)
