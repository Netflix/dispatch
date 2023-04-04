from fastapi import APIRouter, HTTPException, status


from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
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
def get_source_environments(common: CommonParameters):
    """Get all source_environment environments, or only those matching a given search term."""
    return search_filter_sort_paginate(model="SourceEnvironment", **common)


@router.get("/{source_environment_id}", response_model=SourceEnvironmentRead)
def get_source_environment(db_session: DbSession, source_environment_id: PrimaryKey):
    """Given its unique id, retrieve details about a single source_environment environment."""
    source_environment = get(db_session=db_session, source_environment_id=source_environment_id)
    if not source_environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested source environment does not exist."}],
        )
    return source_environment


@router.post("", response_model=SourceEnvironmentRead)
def create_source_environment(
    db_session: DbSession, source_environment_in: SourceEnvironmentCreate
):
    """Creates a new source environment."""
    return create(db_session=db_session, source_environment_in=source_environment_in)


@router.put("/{source_environment_id}", response_model=SourceEnvironmentRead)
def update_source_environment(
    db_session: DbSession,
    source_environment_id: PrimaryKey,
    source_environment_in: SourceEnvironmentUpdate,
):
    """Updates a source environment."""
    source_environment = get(db_session=db_session, source_environment_id=source_environment_id)
    if not source_environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source environment with this id does not exist."}],
        )
    return update(
        db_session=db_session,
        source_environment=source_environment,
        source_environment_in=source_environment_in,
    )


@router.delete("/{source_environment_id}", response_model=None)
def delete_source_environment(db_session: DbSession, source_environment_id: PrimaryKey):
    """Delete a source environment, returning only an HTTP 200 OK if successful."""
    source_environment = get(db_session=db_session, source_environment_id=source_environment_id)
    if not source_environment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A source environment with this id does not exist."}],
        )
    delete(db_session=db_session, source_environment_id=source_environment_id)
