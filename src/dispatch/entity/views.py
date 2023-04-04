from fastapi import APIRouter, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.entity.service import get_cases_with_entity, get_signal_instances_with_entity
from dispatch.models import PrimaryKey

from .models import (
    EntityCreate,
    EntityPagination,
    EntityRead,
    EntityUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=EntityPagination)
def get_entities(common: CommonParameters):
    """Get all entitys, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Entity", **common)


@router.get("/{entity_id}", response_model=EntityRead)
def get_entity(db_session: DbSession, entity_id: PrimaryKey):
    """Given its unique id, retrieve details about a single entity."""
    entity = get(db_session=db_session, entity_id=entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested entity does not exist."}],
        )
    return entity


@router.post("", response_model=EntityRead)
def create_entity(db_session: DbSession, entity_in: EntityCreate):
    """Creates a new entity."""
    return create(db_session=db_session, entity_in=entity_in)


@router.put("/{entity_id}", response_model=EntityRead)
def update_entity(db_session: DbSession, entity_id: PrimaryKey, entity_in: EntityUpdate):
    """Updates an exisiting entity."""
    entity = get(db_session=db_session, entity_id=entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity with this id does not exist."}],
        )
    return update(db_session=db_session, entity=entity, entity_in=entity_in)


@router.delete("/{entity_id}", response_model=None)
def delete_entity(db_session: DbSession, entity_id: PrimaryKey):
    """Deletes a entity, returning only an HTTP 200 OK if successful."""
    entity = get(db_session=db_session, entity_id=entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity with this id does not exist."}],
        )
    delete(db_session=db_session, entity_id=entity_id)


@router.get("/{entity_id}/cases/{days_back}", response_model=None)
def count_cases_with_entity(
    db_session: DbSession,
    entity_id: PrimaryKey,
    days_back: int = 7,
):
    cases = get_cases_with_entity(db_session=db_session, entity_id=entity_id, days_back=days_back)
    return {"cases": cases}


@router.get("/{entity_id}/signal_instances/{days_back}", response_model=None)
def get_signal_instances_by_entity(
    db_session: DbSession,
    entity_id: PrimaryKey,
    days_back: int = 7,
):
    instances = get_signal_instances_with_entity(
        db_session=db_session, entity_id=entity_id, days_back=days_back
    )
    return {"instances": instances}
