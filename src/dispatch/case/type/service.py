from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.sql.expression import true

from dispatch.document import service as document_service
from dispatch.exceptions import NotFoundError
from dispatch.incident.type import service as incident_type_service
from dispatch.project import service as project_service
from dispatch.service import service as service_service

from .models import CaseType, CaseTypeCreate, CaseTypeRead, CaseTypeUpdate


def get(*, db_session, case_type_id: int) -> Optional[CaseType]:
    """Returns a case type based on the given type id."""
    return db_session.query(CaseType).filter(CaseType.id == case_type_id).one_or_none()


def get_default(*, db_session, project_id: int):
    """Returns the default case type."""
    return (
        db_session.query(CaseType)
        .filter(CaseType.default == true())
        .filter(CaseType.project_id == project_id)
        .one_or_none()
    )


def get_default_or_raise(*, db_session, project_id: int) -> CaseType:
    """Returns the default case type or raises a ValidationError if one doesn't exist."""
    case_type = get_default(db_session=db_session, project_id=project_id)

    if not case_type:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="No default case type defined."),
                    loc="case_type",
                )
            ],
            model=CaseTypeRead,
        )
    return case_type


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[CaseType]:
    """Returns a case type based on the given type name."""
    return (
        db_session.query(CaseType)
        .filter(CaseType.name == name)
        .filter(CaseType.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session, project_id: int, case_type_in=CaseTypeRead) -> CaseType:
    """Returns the case type specified or raises a ValidationError."""
    case_type = get_by_name(db_session=db_session, project_id=project_id, name=case_type_in.name)

    if not case_type:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="Case type not found.", case_type=case_type_in.name),
                    loc="case_type",
                )
            ],
            model=CaseTypeRead,
        )

    return case_type


def get_by_name_or_default(*, db_session, project_id: int, case_type_in=CaseTypeRead) -> CaseType:
    """Returns a case type based on a name or the default if not specified."""
    if case_type_in:
        if case_type_in.name:
            return get_by_name_or_raise(
                db_session=db_session, project_id=project_id, case_type_in=case_type_in
            )
    return get_default_or_raise(db_session=db_session, project_id=project_id)


def get_by_slug(*, db_session, project_id: int, slug: str) -> Optional[CaseType]:
    """Returns a case type based on the given type slug."""
    return (
        db_session.query(CaseType)
        .filter(CaseType.slug == slug)
        .filter(CaseType.project_id == project_id)
        .one_or_none()
    )


def get_all(*, db_session, project_id: int = None) -> List[Optional[CaseType]]:
    """Returns all case types."""
    if project_id:
        return db_session.query(CaseType).filter(CaseType.project_id == project_id)
    return db_session.query(CaseType)


def get_all_enabled(*, db_session, project_id: int = None) -> List[Optional[CaseType]]:
    """Returns all enabled case types."""
    if project_id:
        return (
            db_session.query(CaseType)
            .filter(CaseType.project_id == project_id)
            .filter(CaseType.enabled == true())
        )
    return db_session.query(CaseType).filter(CaseType.enabled == true())


def create(*, db_session, case_type_in: CaseTypeCreate) -> CaseType:
    """Creates a case type."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=case_type_in.project
    )

    case_type = CaseType(
        **case_type_in.dict(
            exclude={"case_template_document", "oncall_service", "incident_type", "project"}
        ),
        project=project,
    )

    if case_type_in.case_template_document:
        case_template_document = document_service.get(
            db_session=db_session, document_id=case_type_in.case_template_document.id
        )
        case_type.case_template_document = case_template_document

    if case_type_in.oncall_service:
        oncall_service = service_service.get(
            db_session=db_session, service_id=case_type_in.oncall_service.id
        )
        case_type.oncall_service = oncall_service

    if case_type_in.incident_type:
        incident_type = incident_type_service.get(
            db_session=db_session, incident_type_id=case_type_in.incident_type.id
        )
        case_type.incident_type = incident_type

    db_session.add(case_type)
    db_session.commit()
    return case_type


def update(*, db_session, case_type: CaseType, case_type_in: CaseTypeUpdate) -> CaseType:
    """Updates a case type."""
    if case_type_in.case_template_document:
        case_template_document = document_service.get(
            db_session=db_session, document_id=case_type_in.case_template_document.id
        )
        case_type.case_template_document = case_template_document

    if case_type_in.oncall_service:
        oncall_service = service_service.get(
            db_session=db_session, service_id=case_type_in.oncall_service.id
        )
        case_type.oncall_service = oncall_service

    if case_type_in.incident_type:
        incident_type = incident_type_service.get(
            db_session=db_session, incident_type_id=case_type_in.incident_type.id
        )
        case_type.incident_type = incident_type

    case_type_data = case_type.dict()

    update_data = case_type_in.dict(
        skip_defaults=True, exclude={"case_template_document", "oncall_service", "incident_type"}
    )

    for field in case_type_data:
        if field in update_data:
            setattr(case_type, field, update_data[field])

    db_session.commit()
    return case_type


def delete(*, db_session, case_type_id: int):
    """Deletes a case type."""
    db_session.query(CaseType).filter(CaseType.id == case_type_id).delete()
    db_session.commit()
