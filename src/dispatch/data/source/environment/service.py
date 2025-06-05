from pydantic import ValidationError

from dispatch.project import service as project_service

from .models import (
    SourceEnvironment,
    SourceEnvironmentCreate,
    SourceEnvironmentUpdate,
    SourceEnvironmentRead,
)


def get(*, db_session, source_environment_id: int) -> SourceEnvironment | None:
    """Gets a source by its id."""
    return (
        db_session.query(SourceEnvironment)
        .filter(SourceEnvironment.id == source_environment_id)
        .one_or_none()
    )


def get_by_name(*, db_session, project_id: int, name: str) -> SourceEnvironment | None:
    """Gets a source by its name."""
    return (
        db_session.query(SourceEnvironment)
        .filter(SourceEnvironment.name == name)
        .filter(SourceEnvironment.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id, source_environment_in=SourceEnvironmentRead
) -> SourceEnvironmentRead:
    """Returns the source specified or raises ValidationError."""
    source = get_by_name(
        db_session=db_session,
        project_id=project_id,
        name=source_environment_in.name,
    )

    if not source:
        raise ValidationError(
            [
                {
                    "loc": ("source",),
                    "msg": f"Source environment not found: {source_environment_in.name}",
                    "type": "value_error",
                    "input": source_environment_in.name,
                }
            ]
        )

    return source


def get_all(*, db_session, project_id: int) -> list[SourceEnvironment | None]:
    """Gets all sources."""
    return db_session.query(SourceEnvironment).filter(SourceEnvironment.project_id == project_id)


def create(*, db_session, source_environment_in: SourceEnvironmentCreate) -> SourceEnvironment:
    """Creates a new source."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=source_environment_in.project
    )
    source_environment = SourceEnvironment(
        **source_environment_in.dict(exclude={"project"}), project=project
    )
    db_session.add(source_environment)
    db_session.commit()
    return source_environment


def get_or_create(
    *, db_session, source_environment_in: SourceEnvironmentCreate
) -> SourceEnvironment:
    """Gets or creates a new source."""
    # prefer the source id if available
    if source_environment_in.id:
        q = db_session.query(SourceEnvironment).filter(
            SourceEnvironment.id == source_environment_in.id
        )
    else:
        q = db_session.query(SourceEnvironment).filter_by(name=source_environment_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(
        db_session=db_session,
        source_environment_in=source_environment_in,
    )


def update(
    *,
    db_session,
    source_environment: SourceEnvironment,
    source_environment_in: SourceEnvironmentUpdate,
) -> SourceEnvironment:
    """Updates an existing source."""
    source_environment_data = source_environment.dict()
    update_data = source_environment_in.dict(exclude_unset=True, exclude={})

    for field in source_environment_data:
        if field in update_data:
            setattr(source_environment, field, update_data[field])

    db_session.commit()
    return source_environment


def delete(*, db_session, source_environment_id: int):
    """Deletes an existing source."""
    source_environment = (
        db_session.query(SourceEnvironment)
        .filter(SourceEnvironment.id == source_environment_id)
        .one_or_none()
    )
    db_session.delete(source_environment)
    db_session.commit()
