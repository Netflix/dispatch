from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

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
    """Get all team contacts."""
    return search_filter_sort_paginate(model="TeamContact", **common)


@router.post("", response_model=TeamContactRead)
def create_team(*, db_session: Session = Depends(get_db), team_contact_in: TeamContactCreate):
    """Create a new team contact."""
    team = get_by_email(
        db_session=db_session, email=team_contact_in.email, project_id=team_contact_in.project.id
    )
    if team:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "A team with this email already exists.",
                    "loc": ["email"],
                    "type": "Exists",
                }
            ],
        )
    team = create(db_session=db_session, team_contact_in=team_contact_in)
    return team


@router.get("/{team_contact_id}", response_model=TeamContactRead)
def get_team(*, db_session: Session = Depends(get_db), team_contact_id: PrimaryKey):
    """Get a team contact."""
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The team with this id does not exist."}],
        )
    return team


@router.put("/{team_contact_id}", response_model=TeamContactRead)
def update_team(
    *,
    db_session: Session = Depends(get_db),
    team_contact_id: PrimaryKey,
    team_contact_in: TeamContactUpdate,
):
    """Update a team contact."""
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The team with this id does not exist."}],
        )
    team = update(db_session=db_session, team_contact=team, team_contact_in=team_contact_in)
    return team


@router.delete("/{team_contact_id}", response_model=TeamContactRead)
def delete_team(*, db_session: Session = Depends(get_db), team_contact_id: PrimaryKey):
    """Delete a team contact."""
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The team with this id does not exist."}],
        )

    delete(db_session=db_session, team_contact_id=team_contact_id)
    return team
