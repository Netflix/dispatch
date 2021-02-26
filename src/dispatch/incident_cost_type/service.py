import math

from datetime import datetime

from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from dispatch.database import SessionLocal
from dispatch.incident.enums import IncidentStatus

from .models import IncidentCostType, IncidentCostTypeCreate, IncidentCostTypeUpdate


def get(*, db_session, incident_cost_type_id: int) -> Optional[IncidentCostType]:
    """
    Gets an incident cost type by its id.
    """
    return (
        db_session.query(IncidentCostType)
        .filter(IncidentCostType.id == incident_cost_type_id)
        .one_or_none()
    )


def get_by_name(*, db_session, incident_cost_type_name: str) -> List[Optional[IncidentCostType]]:
    """
    Gets an incident cost type by its name.
    """
    return db_session.query(IncidentCostType).filter(
        IncidentCostType.name == incident_cost_type_name
    )


def get_all(*, db_session) -> List[Optional[IncidentCostType]]:
    """
    Gets all incident cost types.
    """
    return db_session.query(IncidentCostType)


def create(*, db_session, incident_cost_type_in: IncidentCostTypeCreate) -> IncidentCostType:
    """
    Creates a new incident cost type.
    """
    incident_cost_type = IncidentCostType(**incident_cost_type_in.dict())
    db_session.add(incident_cost_type)
    db_session.commit()
    return incident_cost_type


def update(
    *,
    db_session,
    incident_cost_type: IncidentCostType,
    incident_cost_type_in: IncidentCostTypeUpdate
) -> IncidentCostType:
    """
    Updates an incident cost type.
    """
    incident_cost_data = jsonable_encoder(incident_cost_type)
    update_data = incident_cost_type_in.dict(skip_defaults=True)

    for field in incident_cost_data:
        if field in update_data:
            setattr(incident_cost_type, field, update_data[field])

    db_session.add(incident_cost_type)
    db_session.commit()
    return incident_cost_type


def delete(*, db_session, incident_cost_type_id: int):
    """
    Deletes an existing incident cost type.
    """
    db_session.query(IncidentCostType).filter(IncidentCostType.id == incident_cost_type_id).delete()
    db_session.commit()
