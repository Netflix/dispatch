from fastapi import APIRouter, Depends, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import IncidentTypeCreate, IncidentTypePagination, IncidentTypeRead, IncidentTypeUpdate
from .service import create, get, update


router = APIRouter()


@router.get("", response_model=IncidentTypePagination, tags=["incident_types"])
def get_incident_types(common: CommonParameters):
    """Returns all incident types."""
    return search_filter_sort_paginate(model="IncidentType", **common)


@router.post(
    "",
    response_model=IncidentTypeRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_incident_type(
    db_session: DbSession,
    incident_type_in: IncidentTypeCreate,
):
    """Create a new incident type."""
    incident_type = create(db_session=db_session, incident_type_in=incident_type_in)
    return incident_type


@router.put(
    "/{incident_type_id}",
    response_model=IncidentTypeRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_incident_type(
    db_session: DbSession,
    incident_type_id: PrimaryKey,
    incident_type_in: IncidentTypeUpdate,
):
    """Update an existing incident type."""
    incident_type = get(db_session=db_session, incident_type_id=incident_type_id)
    if not incident_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The incident type with this id does not exist."}],
        )

    incident_type = update(
        db_session=db_session, incident_type=incident_type, incident_type_in=incident_type_in
    )
    return incident_type


@router.get("/{incident_type_id}", response_model=IncidentTypeRead)
def get_incident_type(db_session: DbSession, incident_type_id: PrimaryKey):
    """Get an incident type."""
    incident_type = get(db_session=db_session, incident_type_id=incident_type_id)
    if not incident_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The incident type with this id does not exist."}],
        )
    return incident_type
