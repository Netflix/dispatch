from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import (
    TeamContactCreate,
    TeamContactRead,
    TeamContactUpdate,
    TeamPagination,
)
from .service import create, delete, get, get_by_email, update

router = APIRouter()


@router.get("/", response_model=TeamPagination)
def get_teams(
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
    Get all team contacts.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="TeamContact",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.post("/", response_model=TeamContactRead)
def create_team(*, db_session: Session = Depends(get_db), team_contact_in: TeamContactCreate):
    """
    Create a new team contact.
    """
    team = get_by_email(db_session=db_session, email=team_contact_in.email)
    if team:
        raise HTTPException(status_code=400, detail="The team with this email already exists.")
    team = create(db_session=db_session, team_contact_in=team_contact_in)
    return team


@router.get("/{team_id}", response_model=TeamContactRead)
def get_team(*, db_session: Session = Depends(get_db), team_contact_id: int):
    """
    Get a team contact.
    """
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(status_code=404, detail="The team with this id does not exist.")
    return team


@router.put("/{team_contact_id}", response_model=TeamContactRead)
def update_team(
    *,
    db_session: Session = Depends(get_db),
    team_contact_id: int,
    team_contact_in: TeamContactUpdate,
):
    """
    Update a team contact.
    """
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(status_code=404, detail="The team with this id does not exist.")
    team = update(db_session=db_session, team_contact=team, team_contact_in=team_contact_in)
    return team


@router.delete("/{team_contact_id}", response_model=TeamContactRead)
def delete_team(*, db_session: Session = Depends(get_db), team_contact_id: int):
    """
    Delete a team contact.
    """
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(status_code=404, detail="The team with this id does not exist.")

    delete(db_session=db_session, team_contact_id=team_contact_id)
    return team
