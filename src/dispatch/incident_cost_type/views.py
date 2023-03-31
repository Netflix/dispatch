from fastapi import APIRouter, Depends, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    IncidentCostTypeCreate,
    IncidentCostTypePagination,
    IncidentCostTypeRead,
    IncidentCostTypeUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=IncidentCostTypePagination)
def get_incident_cost_types(common: CommonParameters):
    """Get all incident cost types, or only those matching a given search term."""
    return search_filter_sort_paginate(model="IncidentCostType", **common)


@router.get("/{incident_cost_type_id}", response_model=IncidentCostTypeRead)
def get_incident_cost_type(db_session: DbSession, incident_cost_type_id: PrimaryKey):
    """Get an incident cost type by its id."""
    incident_cost_type = get(db_session=db_session, incident_cost_type_id=incident_cost_type_id)
    if not incident_cost_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident cost type with this id does not exist."}],
        )
    return incident_cost_type


@router.post(
    "",
    response_model=IncidentCostTypeRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_incident_cost_type(db_session: DbSession, incident_cost_type_in: IncidentCostTypeCreate):
    """Create an incident cost type."""
    incident_cost_type = create(db_session=db_session, incident_cost_type_in=incident_cost_type_in)
    return incident_cost_type


@router.put(
    "/{incident_cost_type_id}",
    response_model=IncidentCostTypeRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_incident_cost_type(
    db_session: DbSession,
    incident_cost_type_id: PrimaryKey,
    incident_cost_type_in: IncidentCostTypeUpdate,
):
    """Update an incident cost type by its id."""
    incident_cost_type = get(db_session=db_session, incident_cost_type_id=incident_cost_type_id)
    if not incident_cost_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident cost type with this id does not exist."}],
        )

    if not incident_cost_type.editable:
        raise HTTPException(
            status_code=301,
            detail=[{"msg": "You are not allowed to update this incident cost type."}],
        )

    incident_cost_type = update(
        db_session=db_session,
        incident_cost_type=incident_cost_type,
        incident_cost_type_in=incident_cost_type_in,
    )
    return incident_cost_type


@router.delete(
    "/{incident_cost_type_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_incident_cost_type(
    db_session: DbSession,
    incident_cost_type_id: PrimaryKey,
):
    """Delete an incident cost type, returning only an HTTP 200 OK if successful."""
    incident_cost_type = get(db_session=db_session, incident_cost_type_id=incident_cost_type_id)

    if not incident_cost_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident cost type with this id does not exist."}],
        )

    if not incident_cost_type.editable:
        raise HTTPException(
            status_code=301,
            detail=[{"msg": "You are not allowed to delete this incident cost type."}],
        )

    delete(db_session=db_session, incident_cost_type_id=incident_cost_type_id)
