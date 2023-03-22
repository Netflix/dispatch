from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.sql.expression import true

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service

from .models import Workstream, WorkstreamCreate, WorkstreamRead, WorkstreamUpdate


def get(*, db_session, workstream_id: int) -> Optional[Workstream]:
    """Returns a workstream based on the given type id."""
    return db_session.query(Workstream).filter(Workstream.id == workstream_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[Workstream]:
    """Returns a workstream based on the given type name."""
    return (
        db_session.query(Workstream)
        .filter(Workstream.name == name)
        .filter(Workstream.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id: int, workstream_in=WorkstreamRead
) -> Workstream:
    """Returns a workstream based on the given type name or raises a ValidationError."""
    workstream = get_by_name(db_session=db_session, project_id=project_id, name=workstream_in.name)

    if not workstream:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="Workstream not found.", workstream=workstream_in.name),
                    loc="workstream",
                )
            ],
            model=WorkstreamRead,
        )

    return workstream


def get_all(*, db_session, project_id: int = None) -> List[Optional[Workstream]]:
    """Returns all workstreams."""
    if project_id:
        return db_session.query(Workstream).filter(Workstream.project_id == project_id)
    return db_session.query(Workstream)


def get_all_enabled(*, db_session, project_id: int = None) -> List[Optional[Workstream]]:
    """Returns all enabled workstreams."""
    if project_id:
        return (
            db_session.query(Workstream)
            .filter(Workstream.project_id == project_id)
            .filter(Workstream.enabled == true())
        )
    return db_session.query(Workstream).filter(Workstream.enabled == true())


def create(*, db_session, workstream_in: WorkstreamCreate) -> Workstream:
    """Creates a workstream."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=workstream_in.project
    )

    workstream = Workstream(
        **workstream_in.dict(exclude={"project"}),
        project=project,
    )

    db_session.add(workstream)
    db_session.commit()

    return workstream


def update(*, db_session, workstream: Workstream, workstream_in: WorkstreamUpdate) -> Workstream:
    """Updates a workstream."""
    workstream_data = workstream.dict()

    update_data = workstream_in.dict(skip_defaults=True, exclude={})

    for field in workstream_data:
        if field in update_data:
            setattr(workstream, field, update_data[field])

    db_session.commit()

    return workstream


def delete(*, db_session, workstream_id: int):
    """Deletes a workstream."""
    db_session.query(Workstream).filter(Workstream.id == workstream_id).delete()
    db_session.commit()
