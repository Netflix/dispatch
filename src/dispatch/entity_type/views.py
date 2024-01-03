from typing import Union

from fastapi import APIRouter, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.exc import IntegrityError

from dispatch.database.core import DbSession
from dispatch.exceptions import ExistsError
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey
from dispatch.signal.service import get_signal_instance
from dispatch.signal.models import SignalInstanceRead

from .models import (
    EntityTypeCreate,
    EntityTypePagination,
    EntityTypeRead,
    EntityTypeUpdate,
)
from .flows import recalculate_entity_flow
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=EntityTypePagination)
def get_entity_types(common: CommonParameters):
    """Get all entities, or only those matching a given search term."""
    return search_filter_sort_paginate(model="EntityType", **common)


@router.get("/{entity_type_id}", response_model=EntityTypeRead)
def get_entity_type(db_session: DbSession, entity_type_id: PrimaryKey):
    """Get a entity by its id."""
    entity_type = get(db_session=db_session, entity_type_id=entity_type_id)
    if not entity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity_type with this id does not exist."}],
        )
    return entity_type


@router.post("", response_model=EntityTypeRead)
def create_entity_type(db_session: DbSession, entity_type_in: EntityTypeCreate):
    """Create a new entity."""
    try:
        entity_type = create(db_session=db_session, entity_type_in=entity_type_in)
    except IntegrityError:
        raise ValidationError(
            [ErrorWrapper(ExistsError(msg="An entity with this name already exists."), loc="name")],
            model=EntityTypeCreate,
        ) from None
    return entity_type


@router.put("/recalculate/{entity_type_id}/{signal_instance_id}", response_model=SignalInstanceRead)
def recalculate(
    db_session: DbSession, entity_type_id: PrimaryKey, signal_instance_id: Union[str, PrimaryKey]
):
    """Recalculates the associated entities for a signal instance."""
    entity_type = get(
        db_session=db_session,
        entity_type_id=entity_type_id,
    )
    if not entity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An entity type with this id does not exist."}],
        )

    signal_instance = get_signal_instance(
        db_session=db_session,
        signal_instance_id=signal_instance_id,
    )
    if not signal_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A signal instance with this id does not exist."}],
        )

    return recalculate_entity_flow(
        db_session=db_session,
        entity_type=entity_type,
        signal_instance=signal_instance,
    )


@router.put("/{entity_type_id}", response_model=EntityTypeRead)
def update_entity_type(
    db_session: DbSession,
    entity_type_id: PrimaryKey,
    entity_type_in: EntityTypeUpdate,
):
    """Update an entity."""
    entity_type = get(db_session=db_session, entity_type_id=entity_type_id)
    if not entity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity with this id does not exist."}],
        )

    try:
        entity_type = update(
            db_session=db_session, entity_type=entity_type, entity_type_in=entity_type_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A entity type with this name already exists."), loc="name"
                )
            ],
            model=EntityTypeUpdate,
        ) from None
    return entity_type


@router.put("/{entity_type_id}/process", response_model=EntityTypeRead)
def process_entity_type(
    db_session: DbSession,
    entity_type_id: PrimaryKey,
    entity_type_in: EntityTypeUpdate,
):
    """Process an entity type."""
    entity_type = get(db_session=db_session, entity_type_id=entity_type_id)
    if not entity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity with this id does not exist."}],
        )

    try:
        entity_type = update(
            db_session=db_session, entity_type=entity_type, entity_type_in=entity_type_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A entity type with this name already exists."), loc="name"
                )
            ],
            model=EntityTypeUpdate,
        ) from None
    return entity_type


@router.delete("/{entity_type_id}", response_model=None)
def delete_entity_type(db_session: DbSession, entity_type_id: PrimaryKey):
    """Delete an entity."""
    entity_type = get(db_session=db_session, entity_type_id=entity_type_id)
    if not entity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A entity type with this id does not exist."}],
        )
    delete(db_session=db_session, entity_type_id=entity_type_id)
