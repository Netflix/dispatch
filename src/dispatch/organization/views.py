from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import search_filter_sort_paginate

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
from .service import create, delete, get, get_by_name, update

router = APIRouter()


@router.get("/", response_model=OrganizationPagination)
def get_organizations(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
):
    """
    Get all organizations.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Organization",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.post(
    "/",
    response_model=OrganizationRead,
    dependencies=[Depends(PermissionsDependency([OrganizationOwnerPermission]))],
)
def create_organization(
    *, db_session: Session = Depends(get_db), organization_in: OrganizationCreate
):
    """
    Create a new organization.
    """
    organization = get_by_name(db_session=db_session, name=organization_in.name)
    if organization:
        raise HTTPException(
            status_code=400, detail="The organization with this name already exists."
        )
    organization = create(db_session=db_session, organization_in=organization_in)
    return organization


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(*, db_session: Session = Depends(get_db), organization_id: int):
    """
    Get a organization.
    """
    organization = get(db_session=db_session, organization_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="The organization with this id does not exist.")
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
        raise HTTPException(status_code=404, detail="The organization with this id does not exist.")
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
