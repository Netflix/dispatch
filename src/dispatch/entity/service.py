from typing import Optional

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Query, Session

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from .models import Entity, EntityCreate, EntityRead, EntityUpdate


def get(*, db_session, entity_id: int) -> Optional[Entity]:
    """Gets a entity by its id."""
    return db_session.query(Entity).filter(Entity.id == entity_id).one_or_none()


def get_by_name(*, db_session: Session, project_id: int, name: str) -> Optional[Entity]:
    """Gets a entity by its name."""
    return (
        db_session.query(Entity)
        .filter(Entity.name == name)
        .filter(Entity.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session: Session, project_id: int, entity_in=EntityRead) -> Entity:
    """Returns the entity specified or raises ValidationError."""
    entity = get_by_name(db_session=db_session, project_id=project_id, name=entity_in.name)

    if not entity:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="Entity not found.", entity=entity_in.name),
                    loc="entity",
                )
            ],
            model=EntityRead,
        )

    return entity


def get_all(*, db_session: Session) -> Query:
    """Gets all entitys."""
    return db_session.query(Entity)


def create(*, db_session: Session, entity_in: EntityCreate) -> Entity:
    """Creates a new entity."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=entity_in.project
    )
    entity = Entity(**entity_in.dict(exclude={"project"}), project=project)
    db_session.add(entity)
    db_session.commit()
    return entity


def get_or_create(*, db_session: Session, entity_in: EntityCreate) -> Entity:
    """Gets or creates a new entity."""
    q = (
        db_session.query(Entity)
        .filter(Entity.name == entity_in.name)
        .filter(Entity.project_id == entity_in.project.id)
    )

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, entity_in=entity_in)


def update(*, db_session: Session, entity: Entity, entity_in: EntityUpdate) -> Entity:
    """Updates an entity."""
    entity_data = entity.dict()
    update_data = entity_in.dict(skip_defaults=True)

    for field in entity_data:
        if field in update_data:
            setattr(entity, field, update_data[field])

    db_session.commit()
    return entity


def delete(*, db_session: Session, entity_id: int) -> None:
    """Deletes an entity."""
    entity = db_session.query(Entity).filter(Entity.id == entity_id).one_or_none()
    db_session.delete(entity)
    db_session.commit()
