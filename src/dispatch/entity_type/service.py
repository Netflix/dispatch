from typing import Optional

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Query, Session

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.signal import service as signal_service
from .models import EntityType, EntityTypeCreate, EntityTypeRead, EntityTypeUpdate


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
) -> EntityType:
    """Returns the entity type specified or raises ValidationError."""
    entity_type = get_by_name(
        db_session=db_session, project_id=project_id, name=entity_type_in.name
    )

    if not entity_type:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="Entity not found.", entity_type=entity_type_in.name),
                    loc="entity",
                )
            ],
            model=EntityTypeRead,
        )

    return entity_type


def get_all(*, db_session: Session, scope: str = None) -> Query:
    """Gets all entity types."""
    if scope:
        return db_session.query(EntityType).filter(EntityType.scope == scope)
    return db_session.query(EntityType)


def create(*, db_session: Session, entity_type_in: EntityTypeCreate) -> EntityType:
    """Creates a new entity type."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=entity_type_in.project
    )
    entity_type = EntityType(**entity_type_in.dict(exclude={"project", "signals"}), project=project)

    signals = []
    for signal in entity_type_in.signals:
        signal = signal_service.get(db_session=db_session, signal_id=signal.id)
        signals.append(signal)

    entity_type.signals = signals

    db_session.add(entity_type)
    db_session.commit()
    return entity_type


def get_or_create(*, db_session: Session, entity_type_in: EntityTypeCreate) -> EntityType:
    """Gets or creates a new entity type."""
    q = (
        db_session.query(EntityType)
        .filter(EntityType.name == entity_type_in.name)
        .filter(EntityType.project_id == entity_type_in.project.id)
    )

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, entity_type_in=entity_type_in)


def update(
    *, db_session: Session, entity_type: EntityType, entity_type_in: EntityTypeUpdate
) -> EntityType:
    """Updates an entity type."""
    entity_type_data = entity_type.dict()
    update_data = entity_type_in.dict(skip_defaults=True)

    for field in entity_type_data:
        if field in update_data:
            setattr(entity_type, field, update_data[field])

    signals = []
    for signal in entity_type_in.signals:
        signal = signal_service.get(db_session=db_session, signal_id=signal.id)
        signals.append(signal)

    entity_type.signals = signals

    db_session.commit()
    return entity_type


def delete(*, db_session: Session, entity_type_id: int) -> None:
    """Deletes an entity type."""
    entity_type = db_session.query(EntityType).filter(EntityType.id == entity_type_id).one()
    db_session.delete(entity_type)
    db_session.commit()
