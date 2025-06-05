from pydantic import ValidationError

from dispatch.project import service as project_service

from .models import (
    SourceStatus,
    SourceStatusCreate,
    SourceStatusUpdate,
    SourceStatusRead,
)


def get(*, db_session, source_status_id: int) -> SourceStatus | None:
    """Gets a status by its id."""
    return db_session.query(SourceStatus).filter(SourceStatus.id == source_status_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> SourceStatus | None:
    """Gets a status by its name."""
    return (
        db_session.query(SourceStatus)
        .filter(SourceStatus.name == name)
        .filter(SourceStatus.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id, source_status_in=SourceStatusRead
) -> SourceStatusRead:
    """Returns the status specified or raises ValidationError."""
    status = get_by_name(db_session=db_session, project_id=project_id, name=source_status_in.name)

    if not status:
        raise ValidationError(
            [
                {
                    "loc": ("status",),
                    "msg": f"SourceStatus not found: {source_status_in.name}",
                    "type": "value_error",
                    "input": source_status_in.name,
                }
            ]
        )

    return status


def get_all(*, db_session, project_id: int) -> list[SourceStatus | None]:
    """Gets all sources."""
    return db_session.query(SourceStatus).filter(SourceStatus.project_id == project_id)


def create(*, db_session, source_status_in: SourceStatusCreate) -> SourceStatus:
    """Creates a new status."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=source_status_in.project
    )
    source_status = SourceStatus(**source_status_in.dict(exclude={"project"}), project=project)
    db_session.add(source_status)
    db_session.commit()
    return source_status


def get_or_create(*, db_session, source_status_in: SourceStatusCreate) -> SourceStatus:
    """Gets or creates a new status."""
    # prefer the status id if available
    if source_status_in.id:
        q = db_session.query(SourceStatus).filter(SourceStatus.id == source_status_in.id)
    else:
        q = db_session.query(SourceStatus).filter_by(name=source_status_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(
        db_session=db_session,
        source_status_in=source_status_in,
    )


def update(
    *,
    db_session,
    source_status: SourceStatus,
    source_status_in: SourceStatusUpdate,
) -> SourceStatus:
    """Updates an existing status."""
    source_status_data = source_status.dict()
    update_data = source_status_in.dict(exclude_unset=True, exclude={})

    for field in source_status_data:
        if field in update_data:
            setattr(source_status, field, update_data[field])

    db_session.commit()
    return source_status


def delete(*, db_session, source_status_id: int):
    """Deletes an existing status."""
    source_status = (
        db_session.query(SourceStatus).filter(SourceStatus.id == source_status_id).one_or_none()
    )
    db_session.delete(source_status)
    db_session.commit()
