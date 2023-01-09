from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.auth.models import DispatchUser
from dispatch.auth.permissions import (
    OrganizationOwnerPermission,
    PermissionsDependency,
)
from dispatch.auth.service import get_current_user
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.enums import UserRoles
from dispatch.exceptions import ExistsError
from dispatch.models import PrimaryKey
from dispatch.project import service as project_service
from dispatch.project.flows import project_init_flow
from dispatch.project.models import ProjectCreate

from .models import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    OrganizationPagination,
)
from .service import create, get, get_by_name, update, add_user


router = APIRouter()


@router.get("", response_model=OrganizationPagination)
def get_organizations(common: dict = Depends(common_parameters)):
    """Get all organizations."""
    return search_filter_sort_paginate(model="Organization", **common)


@router.post(
    "",
    response_model=OrganizationRead,
)
def create_organization(
    *,
    db_session: Session = Depends(get_db),
    organization_in: OrganizationCreate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Create a new organization."""
    organization = get_by_name(db_session=db_session, name=organization_in.name)
    if organization:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[{"msg": "An organization with this name already exists."}],
        )

    # we create the organization
    organization = create(db_session=db_session, organization_in=organization_in)

    # add creator as organization owner
    add_user(
        db_session=db_session, organization=organization, user=current_user, role=UserRoles.owner
    )

    # we create the default project
    project_in = ProjectCreate(
        name="default",
        default=True,
        description="Default Dispatch project.",
        organization=organization,
    )
    project = project_service.create(db_session=db_session, project_in=project_in)

    # we initialize the default project
    background_tasks.add_task(
        project_init_flow, project=project, organization_slug=organization.slug
    )

    return organization


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(*, db_session: Session = Depends(get_db), organization_id: PrimaryKey):
    """Get an organization."""
    organization = get(db_session=db_session, organization_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An organization with this id does not exist."}],
        )
    return organization


@router.put(
    "/{organization_id}",
    response_model=OrganizationRead,
    dependencies=[Depends(PermissionsDependency([OrganizationOwnerPermission]))],
)
def update_organization(
    *,
    db_session: Session = Depends(get_db),
    organization_id: PrimaryKey,
    organization_in: OrganizationUpdate,
):
    """Update an organization."""
    organization = get(db_session=db_session, organization_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An organization with this id does not exist."}],
        )
    try:
        organization = update(
            db_session=db_session, organization=organization, organization_in=organization_in
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="An organization with this name already exists."), loc="name"
                )
            ],
            model=OrganizationUpdate,
        )
    return organization
