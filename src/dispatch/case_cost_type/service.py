from sqlalchemy.sql.expression import true
from typing import List, Optional

from dispatch.project import service as project_service

from .models import (
    CaseCostType,
    CaseCostTypeCreate,
    CaseCostTypeUpdate,
)


def get(*, db_session, case_cost_type_id: int) -> Optional[CaseCostType]:
    """Gets an case cost type by its id."""
    return db_session.query(CaseCostType).filter(CaseCostType.id == case_cost_type_id).one_or_none()


def get_default(*, db_session, project_id: int) -> Optional[CaseCostType]:
    """Returns the default case cost type."""
    return (
        db_session.query(CaseCostType)
        .filter(CaseCostType.default == true())
        .filter(CaseCostType.project_id == project_id)
        .one_or_none()
    )


def get_by_name(*, db_session, project_id: int, case_cost_type_name: str) -> Optional[CaseCostType]:
    """Gets an case cost type by its name."""
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
    """Updates an case cost type."""
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
