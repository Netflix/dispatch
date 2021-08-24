from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session


from dispatch.database.core import get_db
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.project.models import ProjectRead
from dispatch.project import service as project_service

from .models import (
    IncidentRoles,
    IncidentRolesCreateUpdate,
)
from .service import create_or_update, get_all_by_role


router = APIRouter()


@router.get("/{incident_role}", response_model=IncidentRoles)
def get_incident_roles(
    *,
    db_session: Session = Depends(get_db),
    incident_role: str,
    project_name: str = Query(..., alias="projectName"),
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
    incident_roles_in: IncidentRolesCreateUpdate,
):
    """Update a incident role mapping by its id."""
    return {
        "policies": create_or_update(db_session=db_session, incident_roles_in=incident_roles_in)
    }
