from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency

from .models import (
    IncidentCostCreate,
    IncidentCostPagination,
    IncidentCostRead,
    IncidentCostUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=IncidentCostPagination)
def get_incident_costs(*, common: dict = Depends(common_parameters)):
    """
    Get all incident costs, or only those matching a given search term.
    """
    return search_filter_sort_paginate(model="IncidentCost", **common)


@router.get("/{incident_cost_id}", response_model=IncidentCostRead)
def get_incident_cost(*, db_session: Session = Depends(get_db), incident_cost_id: int):
    """
    Get an incident cost by id.
    """
    incident_cost = get(db_session=db_session, incident_cost_id=incident_cost_id)
    if not incident_cost:
        raise HTTPException(status_code=404, detail="An incident cost with this id does not exist.")
    return incident_cost


@router.post(
    "",
    response_model=IncidentCostRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_incident_cost(
    *, db_session: Session = Depends(get_db), incident_cost_in: IncidentCostCreate
):
    """
    Create an incident cost.
    """
    incident_cost = create(db_session=db_session, incident_cost_in=incident_cost_in)
    return incident_cost


@router.put(
    "/{incident_cost_id}",
    response_model=IncidentCostRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_incident_cost(
    *,
    db_session: Session = Depends(get_db),
    incident_cost_id: int,
    incident_cost_in: IncidentCostUpdate,
):
    """
    Update an incident cost by id.
    """
    incident_cost = get(db_session=db_session, incident_cost_id=incident_cost_id)
    if not incident_cost:
        raise HTTPException(status_code=404, detail="An incident cost with this id does not exist.")
    incident_cost = update(
        db_session=db_session,
        incident_cost=incident_cost,
        incident_cost_in=incident_cost_in,
    )
    return incident_cost


@router.delete(
    "/{incident_cost_id}",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_incident_cost(*, db_session: Session = Depends(get_db), incident_cost_id: int):
    """
    Delete an incident cost, returning only an HTTP 200 OK if successful.
    """
    incident_cost = get(db_session=db_session, incident_cost_id=incident_cost_id)
    if not incident_cost:
        raise HTTPException(status_code=404, detail="An incident cost with this id does not exist.")
    delete(db_session=db_session, incident_cost_id=incident_cost_id)
