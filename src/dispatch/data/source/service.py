from typing import Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError

from .models import Source, SourceCreate, SourceUpdate, SourceRead


def get(*, db_session, source_id: int) -> Optional[Source]:
    """Gets a source by its id."""
    return db_session.query(Source).filter(Source.id == source_id).one_or_none()


def get_by_name(*, db_session, name: str) -> Optional[Source]:
    """Gets a source by its name."""
    return db_session.query(Source).filter(Source.name == name).one_or_none()


def get_by_name_or_raise(*, db_session, source_in=SourceRead) -> SourceRead:
    """Returns the source specified or raises ValidationError."""
    source = get_by_name(db_session=db_session, name=source_in.name)

    if not source:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Source not found.",
                        source=source_in.name,
                    ),
                    loc="source",
                )
            ],
            model=SourceRead,
        )

    return source


def get_all(*, db_session):
    """Gets all sources."""
    return db_session.query(Source)


def create(*, db_session, source_in: SourceCreate) -> Source:
    """Creates a new source."""
    source = Source(**source_in.dict())
    db_session.add(source)
    db_session.commit()
    return source


def get_or_create(*, db_session, source_in: SourceCreate) -> Source:
    """Gets or creates a new source."""
    # prefer the source id if available
    if source_in.id:
        q = db_session.query(Source).filter(Source.id == source_in.id)
    else:
        q = db_session.query(Source).filter_by(name=source_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, source_in=source_in)


def update(*, db_session, source: Source, source_in: SourceUpdate) -> Source:
    """Updates an existing source."""
    source_data = source.dict()
    update_data = source_in.dict(skip_defaults=True, exclude={})

    for field in source_data:
        if field in update_data:
            setattr(source, field, update_data[field])

    db_session.commit()
    return source


def delete(*, db_session, source_id: int):
    """Deletes an existing source."""
    source = db_session.query(Source).filter(Source.id == source_id).one_or_none()
    db_session.delete(source)
    db_session.commit()
