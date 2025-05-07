import logging
from typing import Optional

from pydantic import ValidationError
from sqlalchemy.orm import Query, Session
from jsonpath_ng import parse
from dispatch.project import service as project_service
from dispatch.signal import service as signal_service
from .models import EntityType, EntityTypeCreate, EntityTypeRead, EntityTypeUpdate

logger = logging.getLogger(__name__)


def get(*, db_session, entity_type_id: int) -> Optional[EntityType]:
    """Gets a entity type by its id."""
    return db_session.query(EntityType).filter(EntityType.id == entity_type_id).one_or_none()


def get_by_name(*, db_session: Session, project_id: int, name: str) -> Optional[EntityType]:
    """Gets a entity type by its name."""
    return (
        db_session.query(EntityType)
        .filter(EntityType.name == name)
        .filter(EntityType.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session: Session, project_id: int, entity_type_in=EntityTypeRead
) -> EntityTypeRead:
    """Returns the entity type specified or raises ValidationError."""
    entity_type = get_by_name(
        db_session=db_session, project_id=project_id, name=entity_type_in.name
    )

    if not entity_type:
        raise ValidationError.from_exception_data(
            "EntityTypeRead",
            [
                {
                    "type": "value_error",
                    "loc": ("entity_type",),
                    "input": entity_type_in.name,
                    "ctx": {"error": ValueError("Entity type not found.")},
                }
            ],
        )

    return entity_type


def get_all(*, db_session: Session, scope: str = None) -> Query:
    """Gets all entity types."""
    if scope:
        return db_session.query(EntityType).filter(EntityType.scope == scope)
    return db_session.query(EntityType)


def create(
    *, db_session: Session, entity_type_in: EntityTypeCreate, case_id: int | None = None
) -> EntityType:
    """Creates a new entity type and extracts entities from existing signal instances."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=entity_type_in.project
    )
    entity_type = EntityType(
        **entity_type_in.dict(exclude={"project", "signals", "jpath"}), project=project
    )

    signals = []
    for signal in entity_type_in.signals:
        signal = signal_service.get(db_session=db_session, signal_id=signal.id)
        signals.append(signal)

    entity_type.signals = signals
    set_jpath(entity_type, entity_type_in)

    db_session.add(entity_type)
    db_session.commit()

    # Extract entities for all relevant signal instances
    from dispatch.signal.models import SignalInstance
    from dispatch.entity.service import find_entities

    if case_id:
        # Get all signal instances for the case
        signal_instances = (
            db_session.query(SignalInstance)
            .filter(SignalInstance.case_id == case_id)
            .limit(100)
            .all()
        )
        # Extract and create entities for these instances using only the new entity_type
        for signal_instance in signal_instances:
            new_entities = find_entities(db_session, signal_instance, [entity_type])
            # Associate new entities with the signal_instance
            for entity in new_entities:
                if entity not in signal_instance.entities:
                    signal_instance.entities.append(entity)

    db_session.commit()

    return entity_type


def get_or_create(
    *, db_session: Session, entity_type_in: EntityTypeCreate, case_id: int | None = None
) -> EntityType:
    """Gets or creates a new entity type."""
    q = (
        db_session.query(EntityType)
        .filter(EntityType.name == entity_type_in.name)
        .filter(EntityType.project_id == entity_type_in.project.id)
    )

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, entity_type_in=entity_type_in, case_id=case_id)


def update(
    *, db_session: Session, entity_type: EntityType, entity_type_in: EntityTypeUpdate
) -> EntityType:
    """Updates an entity type."""
    entity_type_data = entity_type.dict()
    update_data = entity_type_in.dict(exclude={"jpath"}, exclude_unset=True)

    for field in entity_type_data:
        if field in update_data:
            setattr(entity_type, field, update_data[field])

    signals = []
    for signal in entity_type_in.signals:
        signal = signal_service.get(db_session=db_session, signal_id=signal.id)
        signals.append(signal)

    entity_type.signals = signals

    set_jpath(entity_type, entity_type_in)

    db_session.commit()
    return entity_type


def delete(*, db_session: Session, entity_type_id: int) -> None:
    """Deletes an entity type."""
    entity_type = db_session.query(EntityType).filter(EntityType.id == entity_type_id).one()
    db_session.delete(entity_type)
    db_session.commit()


def set_jpath(entity_type: EntityType, entity_type_in: EntityTypeCreate):
    entity_type.jpath = ""
    try:
        parse(entity_type_in.jpath)
        entity_type.jpath = entity_type_in.jpath
    except Exception:
        logger.error(
            f"Failed to parse jPath: {entity_type_in.jpath}. The jPath field will be skipped."
        )
