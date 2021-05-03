from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from .models import (
    TeamContactCreate,
    TeamContactRead,
    TeamContactUpdate,
    TeamPagination,
)
from .service import create, delete, get, get_by_email, update

router = APIRouter()


@router.get("", response_model=TeamPagination)
def get_teams(*, common: dict = Depends(common_parameters)):
    """
    Get all team contacts.
    """
    return search_filter_sort_paginate(model="TeamContact", **common)


@router.post("", response_model=TeamContactRead)
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
