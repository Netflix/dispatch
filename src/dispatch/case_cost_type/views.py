from fastapi import APIRouter, Depends, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    CaseCostTypeCreate,
    CaseCostTypePagination,
    CaseCostTypeRead,
    CaseCostTypeUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=CaseCostTypePagination)
def get_case_cost_types(common: CommonParameters):
    """Get all case cost types, or only those matching a given search term."""
    return search_filter_sort_paginate(model="CaseCostType", **common)


@router.get("/{case_cost_type_id}", response_model=CaseCostTypeRead)
def get_case_cost_type(db_session: DbSession, case_cost_type_id: PrimaryKey):
    """Get an case cost type by its id."""
    case_cost_type = get(db_session=db_session, case_cost_type_id=case_cost_type_id)
    if not case_cost_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An case cost type with this id does not exist."}],
        )
    return case_cost_type


@router.post(
    "",
    response_model=CaseCostTypeRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_case_cost_type(db_session: DbSession, case_cost_type_in: CaseCostTypeCreate):
    """Create an case cost type."""
    case_cost_type = create(db_session=db_session, case_cost_type_in=case_cost_type_in)
    return case_cost_type


@router.put(
    "/{case_cost_type_id}",
    response_model=CaseCostTypeRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_case_cost_type(
    db_session: DbSession,
    case_cost_type_id: PrimaryKey,
    case_cost_type_in: CaseCostTypeUpdate,
):
    """Update an case cost type by its id."""
    case_cost_type = get(db_session=db_session, case_cost_type_id=case_cost_type_id)
    if not case_cost_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An case cost type with this id does not exist."}],
        )

    if not case_cost_type.editable:
        raise HTTPException(
            status_code=301,
            detail=[{"msg": "You are not allowed to update this case cost type."}],
        )

    case_cost_type = update(
        db_session=db_session,
        case_cost_type=case_cost_type,
        case_cost_type_in=case_cost_type_in,
    )
    return case_cost_type


@router.delete(
    "/{case_cost_type_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_case_cost_type(
    db_session: DbSession,
    case_cost_type_id: PrimaryKey,
):
    """Delete an case cost type, returning only an HTTP 200 OK if successful."""
    case_cost_type = get(db_session=db_session, case_cost_type_id=case_cost_type_id)

    if not case_cost_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An case cost type with this id does not exist."}],
        )

    if not case_cost_type.editable:
        raise HTTPException(
            status_code=301,
            detail=[{"msg": "You are not allowed to delete this case cost type."}],
        )

    delete(db_session=db_session, case_cost_type_id=case_cost_type_id)
