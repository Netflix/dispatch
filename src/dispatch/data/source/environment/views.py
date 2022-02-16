from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    SourceEnvironmentCreate,
    SourceEnvironmentPagination,
    SourceEnvironmentRead,
    SourceEnvironmentUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=SourceEnvironmentPagination)
def get_source_environments(*, common: dict = Depends(common_parameters)):
    """Get all source environments, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceEnvironment", **common)


@router.get("/{source_environment_id}", response_model=SourceEnvironmentRead)
def get_source_environment(
    *, db_session: Session = Depends(get_db), source_environment_id: PrimaryKey
):
    """Given its unique ID, retrieve details about a single source environment."""
    source = get(db_session=db_session, source_environment_id=source_environment_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source environment does not exist."}],
        )
    return source


@router.post("", response_model=SourceEnvironmentRead)
def create_source_environment(
    *, db_session: Session = Depends(get_db), source_environment_in: SourceEnvironmentCreate
):
    """Create a new source environment."""
    source = create(db_session=db_session, source_environment_in=source_environment_in)
    return source


@router.put("/{source_environment_id}", response_model=SourceEnvironmentRead)
def update_source_environment(
    *,
    db_session: Session = Depends(get_db),
    source_environment_id: PrimaryKey,
    source_environment_in: SourceEnvironmentUpdate,
):
    """Update a source environment."""
    source = get(db_session=db_session, source_environment_id=source_environment_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source environment with this ID does not exist."}],
        )
    source = update(
        db_session=db_session, source=source, source_environment_in=source_environment_in
    )
    return source


@router.delete("/{source_environment_id}")
def delete_source_environment(
    *, db_session: Session = Depends(get_db), source_environment_id: PrimaryKey
):
    """Delete a source environment, returning only an HTTP 200 OK if successful."""
    source = get(db_session=db_session, source_environment_id=source_environment_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An source environment with this ID does not exist."}],
        )
    delete(db_session=db_session, source_environment_id=source_environment_id)
