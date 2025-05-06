from typing import List, Optional
from datetime import datetime, timezone

from dispatch.case.enums import CostModelType
from dispatch.project import service as project_service

from .config import default_case_cost_type
from .models import (
    CaseCostType,
    CaseCostTypeCreate,
    CaseCostTypeUpdate,
)


def get(*, db_session, case_cost_type_id: int) -> Optional[CaseCostType]:
    """Gets a case cost type by its id."""
    return db_session.query(CaseCostType).filter(CaseCostType.id == case_cost_type_id).one_or_none()


def get_response_cost_type(
    *, db_session, project_id: int, model_type: str
) -> Optional[CaseCostType]:
    """Gets the default response cost type."""
    return (
        db_session.query(CaseCostType)
        .filter(CaseCostType.project_id == project_id)
        .filter(CaseCostType.model_type == model_type)
        .one_or_none()
    )


def get_or_create_response_cost_type(
    *, db_session, project_id: int, model_type: str = CostModelType.new
) -> CaseCostType:
    """Gets or creates the response case cost type."""
    case_cost_type = get_response_cost_type(
        db_session=db_session, project_id=project_id, model_type=model_type
    )

    if not case_cost_type:
        case_cost_type_in = CaseCostTypeCreate(
            name=f"{default_case_cost_type['name']}",
            description=f"{default_case_cost_type['description']} ({model_type} Cost Model)",
            category=default_case_cost_type["category"],
            details=default_case_cost_type["details"],
            editable=default_case_cost_type["editable"],
            project=project_service.get(db_session=db_session, project_id=project_id),
            model_type=model_type,
            created_at=datetime.now(timezone.utc),
        )
        case_cost_type = create(db_session=db_session, case_cost_type_in=case_cost_type_in)

    return case_cost_type


def get_all_response_case_cost_types(
    *, db_session, project_id: int
) -> List[Optional[CaseCostType]]:
    """Returns all response case cost types.

    This function queries the database for all case cost types that are marked as the response cost type.
    The following case cost types that match this description are:
    - CaseCostType with model_type CLASSIC
    - CaseCostType with model_type NEW

    All other case types are not tied to the default response cost type.
    """
    return (
        +db_session.query(CaseCostType)
        .filter(CaseCostType.project_id == project_id)
        .filter(CaseCostType.model_type == CostModelType.classic)
        .one()
        + db_session.query(CaseCostType)
        .filter(CaseCostType.project_id == project_id)
        .filter(CaseCostType.model_type == CostModelType.new)
        .one()
    )


def get_by_name(*, db_session, project_id: int, case_cost_type_name: str) -> Optional[CaseCostType]:
    """Gets a case cost type by its name."""
    return (
        db_session.query(CaseCostType)
        .filter(CaseCostType.name == case_cost_type_name)
        .filter(CaseCostType.project_id == project_id)
        .first()
    )


def get_all(*, db_session) -> List[Optional[CaseCostType]]:
    """Gets all case cost types."""
    return db_session.query(CaseCostType).all()


def create(*, db_session, case_cost_type_in: CaseCostTypeCreate) -> CaseCostType:
    """Creates a new case cost type."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=case_cost_type_in.project
    )
    case_cost_type = CaseCostType(**case_cost_type_in.dict(exclude={"project"}), project=project)
    db_session.add(case_cost_type)
    db_session.commit()
    return case_cost_type


def update(
    *,
    db_session,
    case_cost_type: CaseCostType,
    case_cost_type_in: CaseCostTypeUpdate,
) -> CaseCostType:
    """Updates a case cost type."""
    case_cost_data = case_cost_type.dict()
    update_data = case_cost_type_in.dict(skip_defaults=True)

    for field in case_cost_data:
        if field in update_data:
            setattr(case_cost_type, field, update_data[field])

    db_session.commit()
    return case_cost_type


def delete(*, db_session, case_cost_type_id: int):
    """Deletes an existing case cost type."""
    db_session.query(CaseCostType).filter(CaseCostType.id == case_cost_type_id).delete()
    db_session.commit()
