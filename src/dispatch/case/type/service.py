from sqlalchemy.sql.expression import true

from dispatch.case import service as case_service
from dispatch.case_cost import service as case_cost_service
from dispatch.cost_model import service as cost_model_service
from dispatch.document import service as document_service
from dispatch.incident.type import service as incident_type_service
from dispatch.project import service as project_service
from dispatch.service import service as service_service

from .models import CaseType, CaseTypeCreate, CaseTypeRead, CaseTypeUpdate


def get(*, db_session, case_type_id: int) -> CaseType | None:
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
    """Returns the default case type or raises a ValueError if one doesn't exist."""
    case_type = get_default(db_session=db_session, project_id=project_id)

    if not case_type:
        raise ValueError("No default case type defined.")
    return case_type


def get_by_name(*, db_session, project_id: int, name: str) -> CaseType | None:
    """Returns a case type based on the given type name."""
    return (
        db_session.query(CaseType)
        .filter(CaseType.name == name)
        .filter(CaseType.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session, project_id: int, case_type_in=CaseTypeRead) -> CaseType:
    """Returns the case type specified or raises a ValueError."""
    case_type = get_by_name(db_session=db_session, project_id=project_id, name=case_type_in.name)

    if not case_type:
        raise ValueError(f"Case type not found: {case_type_in.name}")

    return case_type


def get_by_name_or_default(*, db_session, project_id: int, case_type_in=CaseTypeRead) -> CaseType:
    """Returns a case type based on a name or the default if not specified."""
    if case_type_in and case_type_in.name:
        case_type = get_by_name(
            db_session=db_session, project_id=project_id, name=case_type_in.name
        )
        if case_type:
            return case_type
    return get_default_or_raise(db_session=db_session, project_id=project_id)


def get_by_slug(*, db_session, project_id: int, slug: str) -> CaseType | None:
    """Returns a case type based on the given type slug."""
    return (
        db_session.query(CaseType)
        .filter(CaseType.slug == slug)
        .filter(CaseType.project_id == project_id)
        .one_or_none()
    )


def get_all(*, db_session, project_id: int = None) -> list[CaseType | None]:
    """Returns all case types."""
    if project_id:
        return db_session.query(CaseType).filter(CaseType.project_id == project_id)
    return db_session.query(CaseType)


def get_all_enabled(*, db_session, project_id: int = None) -> list[CaseType | None]:
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
    if case_type_in.cost_model:
        cost_model = cost_model_service.get_cost_model_by_id(
            db_session=db_session, cost_model_id=case_type_in.cost_model.id
        )
        case_type.cost_model = cost_model

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
    cost_model = None
    if case_type_in.cost_model:
        cost_model = cost_model_service.get_cost_model_by_id(
            db_session=db_session, cost_model_id=case_type_in.cost_model.id
        )
    should_update_case_cost = case_type.cost_model != cost_model
    case_type.cost_model = cost_model

    # Calculate the cost of all non-closed cases associated with this case type
    cases = case_service.get_all_open_by_case_type(db_session=db_session, case_type_id=case_type.id)
    for case in cases:
        case_cost_service.calculate_case_response_cost(case=case, db_session=db_session)

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
        exclude_unset=True, exclude={"case_template_document", "oncall_service", "incident_type"}
    )

    for field in case_type_data:
        if field in update_data:
            setattr(case_type, field, update_data[field])

    db_session.commit()

    if should_update_case_cost:
        case_cost_service.update_case_response_cost_for_case_type(
            db_session=db_session, case_type=case_type
        )

    return case_type


def delete(*, db_session, case_type_id: int):
    """Deletes a case type."""
    db_session.query(CaseType).filter(CaseType.id == case_type_id).delete()
    db_session.commit()
