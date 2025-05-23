from fastapi import APIRouter, Depends, HTTPException, status
from slugify import slugify
from pydantic import ValidationError

from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import (
    OrganizationOwnerPermission,
    PermissionsDependency,
)
from dispatch.auth.service import CurrentUser
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.enums import UserRoles
from dispatch.models import PrimaryKey
from dispatch.project import flows as project_flows
from dispatch.project import service as project_service
from dispatch.project.models import ProjectCreate

from .models import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    OrganizationPagination,
)
from .service import create, get, get_by_name, get_by_slug, update, add_user


router = APIRouter()


@router.get("", response_model=OrganizationPagination)
def get_organizations(common: CommonParameters):
    """Get all organizations."""
    return search_filter_sort_paginate(model="Organization", **common)


@router.post(
    "",
    response_model=OrganizationRead,
)
def create_organization(
    db_session: DbSession,
    organization_in: OrganizationCreate,
    current_user: CurrentUser,
):
    """Create a new organization."""
    if not organization_in.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "An organization name is required."}],
        )
    organization = get_by_name(db_session=db_session, name=organization_in.name)
    if organization:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[{"msg": "An organization with this name already exists."}],
        )
    if organization_in.id and get(db_session=db_session, organization_id=organization_in.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[{"msg": "An organization with this id already exists."}],
        )
    slug = slugify(organization_in.name, separator="_")
    if get_by_slug(db_session=db_session, slug=slug):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[{"msg": "An organization with this slug already exists."}],
        )
    # we create the organization
    organization = create(db_session=db_session, organization_in=organization_in)

    # we add the creator as organization owner
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
    project_flows.project_init_flow(
        project_id=project.id, organization_slug=organization.slug, db_session=db_session
    )

    return organization


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(db_session: DbSession, organization_id: PrimaryKey):
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
    db_session: DbSession,
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
                {
                    "msg": "An organization with this name already exists.",
                    "loc": "name",
                }
            ],
        ) from None
    return organization
