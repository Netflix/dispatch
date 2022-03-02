from typing import Optional, List
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service

from .models import (
    SourceDataFormat,
    SourceDataFormatCreate,
    SourceDataFormatUpdate,
    SourceDataFormatRead,
)


def get(*, db_session, source_data_format_id: int) -> Optional[SourceDataFormat]:
    """Gets a data source by its id."""
    return (
        db_session.query(SourceDataFormat)
        .filter(SourceDataFormat.id == source_data_format_id)
        .one_or_none()
    )


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[SourceDataFormat]:
    """Gets a source by its name."""
    return (
        db_session.query(SourceDataFormat)
        .filter(SourceDataFormat.name == name)
        .filter(SourceDataFormat.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id, source_data_format_in=SourceDataFormatRead
) -> SourceDataFormatRead:
    """Returns the source specified or raises ValidationError."""
    data_format = get_by_name(
        db_session=db_session, project_id=project_id, name=source_data_format_in.name
    )

    if not data_format:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="SourceDataFormat not found.",
                        source=source_data_format_in.name,
                    ),
                    loc="dataFormat",
                )
            ],
            model=SourceDataFormatRead,
        )

    return data_format


def get_all(*, db_session, project_id: int) -> List[Optional[SourceDataFormat]]:
    """Gets all sources."""
    return db_session.query(SourceDataFormat).filter(SourceDataFormat.project_id == project_id)


def create(*, db_session, source_data_format_in: SourceDataFormatCreate) -> SourceDataFormat:
    """Creates a new source."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=source_data_format_in.project
    )
    source_data_format = SourceDataFormat(
        **source_data_format_in.dict(exclude={"project"}), project=project
    )
    db_session.add(source_data_format)
    db_session.commit()
    return source_data_format


def get_or_create(*, db_session, source_data_format_in: SourceDataFormatCreate) -> SourceDataFormat:
    """Gets or creates a new source."""
    # prefer the source id if available
    if source_data_format_in.id:
        q = db_session.query(SourceDataFormat).filter(
            SourceDataFormat.id == source_data_format_in.id
        )
    else:
        q = db_session.query(SourceDataFormat).filter_by(name=source_data_format_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(
        db_session=db_session,
        source_data_format_in=source_data_format_in,
    )


def update(
    *,
    db_session,
    source_data_format: SourceDataFormat,
    source_data_format_in: SourceDataFormatUpdate,
) -> SourceDataFormat:
    """Updates an existing source."""
    source_data_format_data = source_data_format.dict()
    update_data = source_data_format_in.dict(skip_defaults=True, exclude={})

    for field in source_data_format_data:
        if field in update_data:
            setattr(source_data_format, field, update_data[field])

    db_session.commit()
    return source_data_format


def delete(*, db_session, source_data_format_id: int):
    """Deletes an existing source."""
    source_data_format = (
        db_session.query(SourceDataFormat)
        .filter(SourceDataFormat.id == source_data_format_id)
        .one_or_none()
    )
    db_session.delete(source_data_format)
    db_session.commit()
