from fastapi import APIRouter, Depends, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    IncidentPriorityCreate,
    IncidentPriorityPagination,
    IncidentPriorityRead,
    IncidentPriorityUpdate,
)
from .service import create, get, update


router = APIRouter()


@router.get("", response_model=IncidentPriorityPagination, tags=["incident_priorities"])
def get_incident_priorities(common: CommonParameters):
    """Returns all incident priorities."""
    return search_filter_sort_paginate(model="IncidentPriority", **common)


@router.post(
    "",
    response_model=IncidentPriorityRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_incident_priority(
    db_session: DbSession,
    incident_priority_in: IncidentPriorityCreate,
):
    """Create a new incident priority."""
    incident_priority = create(db_session=db_session, incident_priority_in=incident_priority_in)
    return incident_priority


@router.put(
    "/{incident_priority_id}",
    response_model=IncidentPriorityRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_incident_priority(
    db_session: DbSession,
    incident_priority_id: PrimaryKey,
    incident_priority_in: IncidentPriorityUpdate,
):
    """Update an existing incident priority."""
    incident_priority = get(db_session=db_session, incident_priority_id=incident_priority_id)
    if not incident_priority:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident priority with this id does not exist."}],
        )

    incident_priority = update(
        db_session=db_session,
        incident_priority=incident_priority,
        incident_priority_in=incident_priority_in,
    )
    return incident_priority


@router.get("/{incident_priority_id}", response_model=IncidentPriorityRead)
def get_incident_priority(db_session: DbSession, incident_priority_id: PrimaryKey):
    """Get an incident priority."""
    incident_priority = get(db_session=db_session, incident_priority_id=incident_priority_id)
    if not incident_priority:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident priority with this id does not exist."}],
        )
    return incident_priority
