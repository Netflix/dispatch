from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import (
    IndividualContactCreate,
    IndividualContactPagination,
    IndividualContactRead,
    IndividualContactUpdate,
)
from .service import create, delete, get, get_by_email, update

router = APIRouter()


@router.get("/", response_model=IndividualContactPagination)
def get_individuals(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="field[]"),
    ops: List[str] = Query([], alias="op[]"),
    values: List[str] = Query([], alias="value[]"),
):
    """
    Retrieve individual contacts.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="IndividualContact",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.post("/", response_model=IndividualContactRead)
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


@router.put("/{individual_contact_id}", response_model=IndividualContactRead)
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


@router.delete("/{individual_contact_id}")
def delete_individual(*, db_session: Session = Depends(get_db), individual_contact_id: int):
    """
    Delete a individual contact.
    """
    individual = get(db_session=db_session, individual_contact_id=individual_contact_id)
    if not individual:
        raise HTTPException(status_code=404, detail="The individual with this id does not exist.")

    delete(db_session=db_session, individual_contact_id=individual_contact_id)
