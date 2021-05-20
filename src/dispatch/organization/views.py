from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from dispatch.enums import UserRoles
from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user

from dispatch.auth.permissions import (
    OrganizationOwnerPermission,
    PermissionsDependency,
)

from .models import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    OrganizationPagination,
)
from .service import create, delete, get, get_by_name, update, add_user

router = APIRouter()


@router.get("", response_model=OrganizationPagination)
def get_organizations(common: dict = Depends(common_parameters)):
    """
    Get all organizations.
    """
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
):
    """
    Create a new organization.
    """
    organization = get_by_name(db_session=db_session, name=organization_in.name)
    if organization:
        raise HTTPException(
            status_code=400, detail="An organization with this name already exists."
        )
    organization = create(db_session=db_session, organization_in=organization_in)

    # add creator as organization owner
    add_user(
        db_session=db_session, organization=organization, user=current_user, role=UserRoles.owner
    )

    return organization


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(*, db_session: Session = Depends(get_db), organization_id: int):
    """
    Get a organization.
    """
    organization = get(db_session=db_session, organization_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="An organization with this id does not exist.")
    return organization


@router.put(
    "/{organization_id}",
    response_model=OrganizationRead,
    dependencies=[Depends(PermissionsDependency([OrganizationOwnerPermission]))],
)
def update_organization(
    *,
    db_session: Session = Depends(get_db),
    organization_id: int,
    organization_in: OrganizationUpdate,
):
    """
    Update a organization.
    """
    organization = get(db_session=db_session, organization_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="An organization with this id does not exist.")
    organization = update(
        db_session=db_session, organization=organization, organization_in=organization_in
    )
    return organization


@router.delete(
    "/{organization_id}",
    response_model=OrganizationRead,
    dependencies=[Depends(PermissionsDependency([OrganizationOwnerPermission]))],
)
def delete_organization(*, db_session: Session = Depends(get_db), organization_id: int):
    """
    Delete an organization.
    """
    organization = get(db_session=db_session, organization_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="An organization with this id does not exist.")

    delete(db_session=db_session, organization_id=organization_id)
    return organization
