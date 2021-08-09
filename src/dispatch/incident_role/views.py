from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    IncidentRoleCreate,
    IncidentRolePagination,
    IncidentRoleRead,
    IncidentRoleUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=IncidentRolePagination)
def get_incident_roles(*, common: dict = Depends(common_parameters)):
    """Get all incident role mappings."""
    return search_filter_sort_paginate(model="IncidentRole", **common)


@router.get("/{incident_role_id}", response_model=IncidentRoleRead)
def get_incident_role(*, db_session: Session = Depends(get_db), incident_role_id: PrimaryKey):
    """Get a incident role mapping by its id."""
    incident_role = get(db_session=db_session, incident_role_id=incident_role_id)
    if not incident_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A incident role mapping with this id does not exist."}],
        )
    return incident_role


@router.post(
    "",
    response_model=IncidentRoleRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_incident_role(
    *,
    db_session: Session = Depends(get_db),
    incident_role_in: IncidentRoleCreate,
):
    """Create a incident role."""
    incident_role = create(db_session=db_session, incident_role_in=incident_role_in)
    return incident_role


@router.put(
    "/{incident_role_id}",
    response_model=IncidentRoleRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_incident_role(
    *,
    db_session: Session = Depends(get_db),
    incident_role_id: PrimaryKey,
    incident_role_in: IncidentRoleUpdate,
):
    """Update a incident role mapping by its id."""
    incident_role = get(db_session=db_session, incident_role_id=incident_role_id)
    if not incident_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A incident role mapping with this id does not exist."}],
        )
    incident_role = update(
        db_session=db_session,
        incident_role=incident_role,
        incident_role_in=incident_role_in,
    )
    return incident_role


@router.delete(
    "/{incident_role_id}",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_incident_role(*, db_session: Session = Depends(get_db), incident_role_id: PrimaryKey):
    """Delete a incident role mapping, returning only an HTTP 200 OK if successful."""
    incident_role = get(db_session=db_session, incident_role_id=incident_role_id)
    if not incident_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A incident role mapping with this id does not exist."}],
        )
    delete(db_session=db_session, incident_role_id=incident_role_id)
