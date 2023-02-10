from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.exceptions import ExistsError
from dispatch.database.service import common_parameters, search_filter_sort_paginate
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
def get_entities(*, common: dict = Depends(common_parameters)):
    """Get all entities, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Entity", **common)


@router.get("/{entity_id}", response_model=EntityRead)
def get_entity(*, db_session: Session = Depends(get_db), entity_id: PrimaryKey):
    """Get a entity by its id."""
    entity = get(db_session=db_session, entity_id=entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity with this id does not exist."}],
        )
    return entity


@router.post("", response_model=EntityRead)
def create_entity(*, db_session: Session = Depends(get_db), entity_in: EntityCreate):
    """Create a new entity."""
    try:
        entity = create(db_session=db_session, entity_in=entity_in)
    except IntegrityError:
        raise ValidationError(
            [ErrorWrapper(ExistsError(msg="A entity with this name already exists."), loc="name")],
            model=EntityCreate,
        )
    return entity


@router.put("/{entity_id}", response_model=EntityRead)
def update_entity(
    *, db_session: Session = Depends(get_db), entity_id: PrimaryKey, entity_in: EntityUpdate
):
    """Update an entity."""
    entity = get(db_session=db_session, entity_id=entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity with this id does not exist."}],
        )

    try:
        entity = update(db_session=db_session, entity=entity, entity_in=entity_in)
    except IntegrityError:
        raise ValidationError(
            [ErrorWrapper(ExistsError(msg="A entity with this name already exists."), loc="name")],
            model=EntityUpdate,
        )
    return entity


@router.delete("/{entity_id}", response_model=None)
def delete_entity(*, db_session: Session = Depends(get_db), entity_id: PrimaryKey):
    """Delete an entity."""
    entity = get(db_session=db_session, entity_id=entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity with this id does not exist."}],
        )
    delete(db_session=db_session, entity_id=entity_id)
