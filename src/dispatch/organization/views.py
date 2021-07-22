from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from dispatch.enums import UserRoles
from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user

from dispatch.auth.permissions import (
    OrganizationOwnerPermission,
    PermissionsDependency,
)
from dispatch.models import PrimaryKey

from .models import (
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
    OrganizationPagination,
)
from .service import create, get, update, add_user

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
):
    """Create a new organization."""
    try:
        organization = create(db_session=db_session, organization_in=organization_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "An organization with this name already exists.",
                    "loc": ["name"],
                    "type": "Exists",
                }
            ],
        )

    # add creator as organization owner
    add_user(
        db_session=db_session, organization=organization, user=current_user, role=UserRoles.owner
    )

    return organization


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(*, db_session: Session = Depends(get_db), organization_id: int):
    """Get an organization."""
    organization = get(db_session=db_session, organization_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=404, detail=[{"msg": "An organization with this id does not exist."}]
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
            status_code=404, detail=[{"msg": "An organization with this id does not exist."}]
        )
    organization = update(
        db_session=db_session, organization=organization, organization_in=organization_in
    )
    return organization


# this isn't full supported yet
# @router.delete(
#    "/{organization_id}",
#    response_model=OrganizationRead,
#    dependencies=[Depends(PermissionsDependency([OrganizationOwnerPermission]))],
# )
# def delete_organization(*, db_session: Session = Depends(get_db), organization_id: PrimaryKey):
#    """Delete an organization."""
#    organization = get(db_session=db_session, organization_id=organization_id)
#    if not organization:
#        raise HTTPException(
#            status_code=404, detail=[{"msg": "An organization with this id does not exist."}]
#        )
#
#    delete(db_session=db_session, organization_id=organization_id)
#    return organization
#
