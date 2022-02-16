from typing import Optional, List
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError

from .models import (
    SourceStatus,
    SourceStatusCreate,
    SourceStatusUpdate,
    SourceStatusRead,
)


def get(*, db_session, source_type_id: int) -> Optional[SourceStatus]:
    """Gets a source by its id."""
    return db_session.query(SourceStatus).filter(SourceStatus.id == source_type_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[SourceStatus]:
    """Gets a source by its name."""
    return (
        db_session.query(SourceStatus)
        .filter(SourceStatus.name == name)
        .filter(SourceStatus.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id, source_type_in=SourceStatusRead
) -> SourceStatusRead:
    """Returns the source specified or raises ValidationError."""
    source = get_by_name(db_session=db_session, project_id=project_id, name=source_type_in.name)

    if not source:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="SourceStatus not found.",
                        source=source_type_in.name,
                    ),
                    loc="source",
                )
            ],
            SourceStatus=SourceStatusRead,
        )

    return source


def get_all(*, db_session, project_id: int) -> List[Optional[SourceStatus]]:
    """Gets all sources."""
    return db_session.query(SourceStatus).filter(SourceStatus.project_id == project_id)


def create(*, db_session, source_type_in: SourceStatusCreate) -> SourceStatus:
    """Creates a new source."""
    source_type = SourceStatus(**source_type_in.dict())
    db_session.add(source_type)
    db_session.commit()
    return source_type


def get_or_create(*, db_session, source_type_in: SourceStatusCreate) -> SourceStatus:
    """Gets or creates a new source."""
    # prefer the source id if available
    if source_type_in.id:
        q = db_session.query(SourceStatus).filter(SourceStatus.id == source_type_in.id)
    else:
        q = db_session.query(SourceStatus).filter_by(name=source_type_in.name)

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
    source_type: SourceStatus,
    source_type_in: SourceStatusUpdate,
) -> SourceStatus:
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
    source_type = (
        db_session.query(SourceStatus).filter(SourceStatus.id == source_type_id).one_or_none()
    )
    db_session.delete(source_type)
    db_session.commit()
