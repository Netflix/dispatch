from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from dispatch.case.service import get as get_case
from dispatch.database.core import DbSession
from dispatch.exceptions import ExistsError
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey
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
            [
                {
                    "msg": "An entity with this name already exists.",
                    "loc": "name",
                }
            ]
        )
    return entity_type


@router.post("/{case_id}", response_model=EntityTypeRead)
def create_entity_type_with_case(
    db_session: DbSession, case_id: PrimaryKey, entity_type_in: EntityTypeCreate
):
    """Create a new entity."""
    try:
        entity_type = create(db_session=db_session, entity_type_in=entity_type_in, case_id=case_id)
    except IntegrityError:
        raise ValidationError(
            [
                {
                    "msg": "An entity with this name already exists.",
                    "loc": "name",
                }
            ]
        )
    return entity_type


@router.put("/recalculate/{entity_type_id}/{case_id}", response_model=List[SignalInstanceRead])
def recalculate(db_session: DbSession, entity_type_id: PrimaryKey, case_id: PrimaryKey):
    """Recalculates the associated entities for all signal instances in a case."""
    entity_type = get(
        db_session=db_session,
        entity_type_id=entity_type_id,
    )
    if not entity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An entity type with this id does not exist."}],
        )

    case = get_case(db_session=db_session, case_id=case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A case with this id does not exist."}],
        )

    # Get all signal instances associated with the case
    signal_instances = case.signal_instances
    if not signal_instances:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "No signal instances found for this case."}],
        )

    # Recalculate entities for each signal instance
    updated_signal_instances = []
    for signal_instance in signal_instances:
        updated_signal_instance = recalculate_entity_flow(
            db_session=db_session,
            entity_type=entity_type,
            signal_instance=signal_instance,
        )
        updated_signal_instances.append(updated_signal_instance)

    return updated_signal_instances


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
                {
                    "msg": "An entity with this name already exists.",
                    "loc": "name",
                }
            ]
        )
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
                {
                    "msg": "An entity with this name already exists.",
                    "loc": "name",
                }
            ]
        )
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
