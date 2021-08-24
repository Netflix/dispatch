from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.project.models import ProjectRead
from dispatch.project import service as project_service

from .models import (
    IncidentRoles,
)
from .service import get, update, get_all_by_role


router = APIRouter()


@router.get("/{incident_role}", response_model=IncidentRoles)
def get_incident_roles(
    *, db_session: Session = Depends(get_db), incident_role: str, project_name: str
):
    """Get all incident role mappings."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=ProjectRead(name=project_name)
    )
    policies = get_all_by_role(db_session=db_session, role=incident_role, project_id=project.id)
    return {"policies": policies}


@router.put(
    "/{incident_role}",
    response_model=IncidentRoles,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_incident_role(
    *,
    db_session: Session = Depends(get_db),
    incident_role: str,
    incident_roles_in: IncidentRoles,
):
    """Update a incident role mapping by its id."""
    incident_roles = [
        get(db_session=db_session, incident_role_id=i["id"]) for i in incident_roles_in
    ]
    if not incident_roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A incident role mapping with this id does not exist."}],
        )
    incident_roles = update(
        db_session=db_session,
        incident_role=incident_role,
        incident_roles_in=incident_roles_in,
    )
    return incident_roles
