from sqlalchemy.sql.expression import true
from typing import List, Optional

from dispatch.project import service as project_service

from .models import (
    IncidentCostType,
    IncidentCostTypeCreate,
    IncidentCostTypeUpdate,
)


def get(*, db_session, incident_cost_type_id: int) -> Optional[IncidentCostType]:
    """Gets an incident cost type by its id."""
    return (
        db_session.query(IncidentCostType)
        .filter(IncidentCostType.id == incident_cost_type_id)
        .one_or_none()
    )


def get_default(*, db_session, project_id: int) -> Optional[IncidentCostType]:
    """Returns the default incident cost type."""
    return (
        db_session.query(IncidentCostType)
        .filter(IncidentCostType.default == true())
        .filter(IncidentCostType.project_id == project_id)
        .one_or_none()
    )


def get_by_name(
    *, db_session, project_id: int, incident_cost_type_name: str
) -> Optional[IncidentCostType]:
    """Gets an incident cost type by its name."""
    return (
        db_session.query(IncidentCostType)
        .filter(IncidentCostType.name == incident_cost_type_name)
        .filter(IncidentCostType.project_id == project_id)
        .first()
    )


def get_all(*, db_session) -> List[Optional[IncidentCostType]]:
    """Gets all incident cost types."""
    return db_session.query(IncidentCostType).all()


def create(*, db_session, incident_cost_type_in: IncidentCostTypeCreate) -> IncidentCostType:
    """Creates a new incident cost type."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=incident_cost_type_in.project
    )
    incident_cost_type = IncidentCostType(
        **incident_cost_type_in.dict(exclude={"project"}), project=project
    )
    db_session.add(incident_cost_type)
    db_session.commit()
    return incident_cost_type


def update(
    *,
    db_session,
    incident_cost_type: IncidentCostType,
    incident_cost_type_in: IncidentCostTypeUpdate,
) -> IncidentCostType:
    """Updates an incident cost type."""
    incident_cost_data = incident_cost_type.dict()
    update_data = incident_cost_type_in.dict(skip_defaults=True)

    for field in incident_cost_data:
        if field in update_data:
            setattr(incident_cost_type, field, update_data[field])

    db_session.commit()
    return incident_cost_type


def delete(*, db_session, incident_cost_type_id: int):
    """Deletes an existing incident cost type."""
    db_session.query(IncidentCostType).filter(IncidentCostType.id == incident_cost_type_id).delete()
    db_session.commit()
