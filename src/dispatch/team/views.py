from fastapi import APIRouter, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.database.core import DbSession
from dispatch.exceptions import ExistsError
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
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
def get_teams(common: CommonParameters):
    """Get all team contacts."""
    return search_filter_sort_paginate(model="TeamContact", **common)


@router.post("", response_model=TeamContactRead)
def create_team(db_session: DbSession, team_contact_in: TeamContactCreate):
    """Create a new team contact."""
    team = get_by_email(
        db_session=db_session, email=team_contact_in.email, project_id=team_contact_in.project.id
    )
    if team:
        raise ValidationError(
            [ErrorWrapper(ExistsError(msg="A team with this name already exists."), loc="name")],
            model=TeamContactCreate,
        )
    return create(db_session=db_session, team_contact_in=team_contact_in)


@router.get("/{team_contact_id}", response_model=TeamContactRead)
def get_team(db_session: DbSession, team_contact_id: PrimaryKey):
    """Get a team contact."""
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A team with this id does not exist."}],
        )
    return team


@router.put("/{team_contact_id}", response_model=TeamContactRead)
def update_team(
    db_session: DbSession,
    team_contact_id: PrimaryKey,
    team_contact_in: TeamContactUpdate,
):
    """Update a team contact."""
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A team with this id does not exist."}],
        )
    return update(db_session=db_session, team_contact=team, team_contact_in=team_contact_in)


@router.delete("/{team_contact_id}", response_model=None)
def delete_team(db_session: DbSession, team_contact_id: PrimaryKey):
    """Delete a team contact."""
    team = get(db_session=db_session, team_contact_id=team_contact_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A team with this id does not exist."}],
        )
    delete(db_session=db_session, team_contact_id=team_contact_id)
