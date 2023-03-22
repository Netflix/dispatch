from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.sql.expression import true

from dispatch.document import service as document_service
from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.service import service as service_service

from .models import WorkstreamType, WorkstreamTypeCreate, WorkstreamTypeRead, WorkstreamTypeUpdate


def get(*, db_session, workstream_type_id: int) -> Optional[WorkstreamType]:
    """Returns a workstream type based on the given type id."""
    return (
        db_session.query(WorkstreamType)
        .filter(WorkstreamType.id == workstream_type_id)
        .one_or_none()
    )


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[WorkstreamType]:
    """Returns a workstream type based on the given type name."""
    return (
        db_session.query(WorkstreamType)
        .filter(WorkstreamType.name == name)
        .filter(WorkstreamType.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id: int, workstream_type_in=WorkstreamTypeRead
) -> WorkstreamType:
    """Returns a workstream type based on the given type name or raises a ValidationError."""
    workstream_type = get_by_name(
        db_session=db_session, project_id=project_id, name=workstream_type_in.name
    )

    if not workstream_type:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Workstream type not found.", workstream_type=workstream_type_in.name
                    ),
                    loc="workstream_type",
                )
            ],
            model=WorkstreamTypeRead,
        )

    return workstream_type


def get_all(*, db_session, project_id: int = None) -> List[Optional[WorkstreamType]]:
    """Returns all workstream types."""
    if project_id:
        return db_session.query(WorkstreamType).filter(WorkstreamType.project_id == project_id)
    return db_session.query(WorkstreamType)


def get_all_enabled(*, db_session, project_id: int = None) -> List[Optional[WorkstreamType]]:
    """Returns all enabled workstream types."""
    if project_id:
        return (
            db_session.query(WorkstreamType)
            .filter(WorkstreamType.project_id == project_id)
            .filter(WorkstreamType.enabled == true())
        )
    return db_session.query(WorkstreamType).filter(WorkstreamType.enabled == true())


def create(*, db_session, workstream_type_in: WorkstreamTypeCreate) -> WorkstreamType:
    """Creates a workstream type."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=workstream_type_in.project
    )

    workstream_type = WorkstreamType(
        **workstream_type_in.dict(exclude={"document_template", "oncall_service", "project"}),
        project=project,
    )

    if workstream_type_in.document_template:
        document_template = document_service.get(
            db_session=db_session, document_id=workstream_type_in.document_template.id
        )
        workstream_type.document_template = document_template

    if workstream_type_in.oncall_service:
        oncall_service = service_service.get(
            db_session=db_session, service_id=workstream_type_in.oncall_service.id
        )
        workstream_type.oncall_service = oncall_service

    db_session.add(workstream_type)
    db_session.commit()

    return workstream_type


def update(
    *, db_session, workstream_type: WorkstreamType, workstream_type_in: WorkstreamTypeUpdate
) -> WorkstreamType:
    """Updates a workstream type."""
    if workstream_type_in.document_template:
        document_template = document_service.get(
            db_session=db_session, document_id=workstream_type_in.document_template.id
        )
        workstream_type.document_template = document_template

    if workstream_type_in.oncall_service:
        oncall_service = service_service.get(
            db_session=db_session, service_id=workstream_type_in.oncall_service.id
        )
        workstream_type.oncall_service = oncall_service

    workstream_type_data = workstream_type.dict()

    update_data = workstream_type_in.dict(
        skip_defaults=True, exclude={"document_template", "oncall_service"}
    )

    for field in workstream_type_data:
        if field in update_data:
            setattr(workstream_type, field, update_data[field])

    db_session.commit()

    return workstream_type


def delete(*, db_session, workstream_type_id: int):
    """Deletes a workstream type."""
    db_session.query(WorkstreamType).filter(WorkstreamType.id == workstream_type_id).delete()
    db_session.commit()
