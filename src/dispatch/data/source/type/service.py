from typing import Optional, List
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service

from .models import (
    SourceType,
    SourceTypeCreate,
    SourceTypeUpdate,
    SourceTypeRead,
)


def get(*, db_session, source_type_id: int) -> Optional[SourceType]:
    """Gets a source by its id."""
    return db_session.query(SourceType).filter(SourceType.id == source_type_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[SourceType]:
    """Gets a source by its name."""
    return (
        db_session.query(SourceType)
        .filter(SourceType.name == name)
        .filter(SourceType.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id, source_type_in=SourceTypeRead
) -> SourceTypeRead:
    """Returns the source specified or raises ValidationError."""
    source = get_by_name(db_session=db_session, project_id=project_id, name=source_type_in.name)

    if not source:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="SourceType not found.",
                        source=source_type_in.name,
                    ),
                    loc="source",
                )
            ],
            model=SourceTypeRead,
        )

    return source


def get_all(*, db_session, project_id: int) -> List[Optional[SourceType]]:
    """Gets all source types."""
    return db_session.query(SourceType).filter(SourceType.project_id == project_id)


def create(*, db_session, source_type_in: SourceTypeCreate) -> SourceType:
    """Creates a new source type."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=source_type_in.project
    )
    source_type = SourceType(**source_type_in.dict(exclude={"project"}), project=project)
    db_session.add(source_type)
    db_session.commit()
    return source_type


def get_or_create(*, db_session, source_type_in: SourceTypeCreate) -> SourceType:
    """Gets or creates a new source type."""
    # prefer the source id if available
    if source_type_in.id:
        q = db_session.query(SourceType).filter(SourceType.id == source_type_in.id)
    else:
        q = db_session.query(SourceType).filter_by(name=source_type_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(
        db_session=db_session,
        source_type_in=source_type_in,
    )


def update(
    *,
    db_session,
    source_type: SourceType,
    source_type_in: SourceTypeUpdate,
) -> SourceType:
    """Updates an existing source."""
    source_type_data = source_type.dict()
    update_data = source_type_in.dict(skip_defaults=True, exclude={})

    for field in source_type_data:
        if field in update_data:
            setattr(source_type, field, update_data[field])

    db_session.commit()
    return source_type


def delete(*, db_session, source_type_id: int):
    """Deletes an existing source."""
    source_type = db_session.query(SourceType).filter(SourceType.id == source_type_id).one_or_none()
    db_session.delete(source_type)
    db_session.commit()
