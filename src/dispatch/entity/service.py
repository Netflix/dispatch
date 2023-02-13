from datetime import datetime, timedelta
from typing import Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Session

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.case.models import Case
from dispatch.entity.models import Entity
from dispatch.entity_type import service as entity_type_service
from dispatch.signal.models import SignalInstance

from .models import Entity, EntityCreate, EntityUpdate, EntityRead


def get(*, db_session, entity_id: int) -> Optional[Entity]:
    """Gets a entity by its id."""
    return db_session.query(Entity).filter(Entity.id == entity_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[Entity]:
    """Gets a entity by its project and name."""
    return (
        db_session.query(Entity)
        .filter(Entity.name == name)
        .filter(Entity.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session, project_id: int, entity_in=EntityRead) -> EntityRead:
    """Returns the entity specified or raises ValidationError."""
    entity = get_by_name(db_session=db_session, project_id=project_id, name=entity_in.name)

    if not entity:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Entity not found.",
                        entity=entity_in.name,
                    ),
                    loc="entity",
                )
            ],
            model=EntityRead,
        )

    return entity


def get_by_value(*, db_session, project_id: int, value: str) -> Optional[Entity]:
    """Gets a entity by its value."""
    return (
        db_session.query(Entity)
        .filter(Entity.value == value)
        .filter(Entity.project_id == project_id)
        .one_or_none()
    )


def get_all(*, db_session, project_id: int):
    """Gets all entities by their project."""
    return db_session.query(Entity).filter(Entity.project_id == project_id)


def create(*, db_session, entity_in: EntityCreate) -> Entity:
    """Creates a new entity."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=entity_in.project
    )
    entity_type = entity_type_service.get_or_create(
        db_session=db_session, entity_type_in=entity_in.entity_type
    )
    entity = Entity(
        **entity_in.dict(exclude={"entity_type", "project"}),
        project=project,
        entity_type=entity_type,
    )
    entity.entity_type = entity_type
    entity.project = project
    db_session.add(entity)
    db_session.commit()
    return entity


def get_by_value_or_create(*, db_session, entity_in: EntityCreate) -> Entity:
    """Gets or creates a new entity."""
    # prefer the entity id if available
    if entity_in.id:
        q = db_session.query(Entity).filter(Entity.id == entity_in.id)
    else:
        q = db_session.query(Entity).filter_by(value=entity_in.value)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, entity_in=entity_in)


def update(*, db_session, entity: Entity, entity_in: EntityUpdate) -> Entity:
    """Updates an existing entity."""
    entity_data = entity.dict()
    update_data = entity_in.dict(skip_defaults=True, exclude={"entity_type"})

    for field in entity_data:
        if field in update_data:
            setattr(entity, field, update_data[field])

    if entity_in.entity_type is not None:
        entity_type = entity_type_service.get_by_name_or_raise(
            db_session=db_session,
            project_id=entity.project.id,
            entity_type_in=entity_in.entity_type,
        )
        entity.entity_type = entity_type

    db_session.commit()
    return entity


def delete(*, db_session, entity_id: int):
    """Deletes an existing entity."""
    entity = db_session.query(Entity).filter(Entity.id == entity_id).one_or_none()
    db_session.delete(entity)
    db_session.commit()


def get_cases_with_entity(db: Session, entity_id: int, days_back: int) -> int:
    start_date = datetime.utcnow() - timedelta(days=days_back)
    cases = (
        db.query(Case)
        .join(Case.signal_instances)
        .join(SignalInstance.entities)
        .filter(Entity.id == entity_id, SignalInstance.created_at >= start_date)
        .all()
    )
    return cases


def get_signal_instances_with_entity(
    db: Session, entity_id: int, days_back: int
) -> list[SignalInstance]:
    """
    Searches for signal instances with the same entity within a given timeframe.
    """
    # Calculate the datetime for the start of the search window
    start_date = datetime.utcnow() - timedelta(days=days_back)

    # Query for signal instances containing the entity within the search window
    signal_instances = (
        db.query(SignalInstance)
        .join(SignalInstance.entities)
        .filter(SignalInstance.created_at >= start_date, Entity.id == entity_id)
        .all()
    )

    return signal_instances
