from fastapi import APIRouter, Depends, HTTPException, status

from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    IncidentSeverityCreate,
    IncidentSeverityPagination,
    IncidentSeverityRead,
    IncidentSeverityUpdate,
)
from .service import create, get, update


router = APIRouter()


@router.get("", response_model=IncidentSeverityPagination, tags=["incident_severities"])
def get_incident_severities(common: CommonParameters):
    """Returns all incident severities."""
    return search_filter_sort_paginate(model="IncidentSeverity", **common)


@router.post(
    "",
    response_model=IncidentSeverityRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_incident_severity(
    db_session: DbSession,
    incident_severity_in: IncidentSeverityCreate,
):
    """Creates a new incident severity."""
    incident_severity = create(db_session=db_session, incident_severity_in=incident_severity_in)
    return incident_severity


@router.put(
    "/{incident_severity_id}",
    response_model=IncidentSeverityRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_incident_severity(
    db_session: DbSession,
    incident_severity_id: PrimaryKey,
    incident_severity_in: IncidentSeverityUpdate,
):
    """Updates an existing incident severity."""
    incident_severity = get(db_session=db_session, incident_severity_id=incident_severity_id)
    if not incident_severity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident severity with this id does not exist."}],
        )

    incident_severity = update(
        db_session=db_session,
        incident_severity=incident_severity,
        incident_severity_in=incident_severity_in,
    )
    return incident_severity


@router.get("/{incident_severity_id}", response_model=IncidentSeverityRead)
def get_incident_severity(db_session: DbSession, incident_severity_id: PrimaryKey):
    """Gets an incident severity."""
    incident_severity = get(db_session=db_session, incident_severity_id=incident_severity_id)
    if not incident_severity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident severity with this id does not exist."}],
        )
    return incident_severity
