from fastapi import APIRouter, Depends, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    CaseCostCreate,
    CaseCostPagination,
    CaseCostRead,
    CaseCostUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=CaseCostPagination)
def get_case_costs(common: CommonParameters):
    """Get all case costs, or only those matching a given search term."""
    return search_filter_sort_paginate(model="CaseCost", **common)


@router.get("/{case_cost_id}", response_model=CaseCostRead)
def get_case_cost(db_session: DbSession, case_cost_id: PrimaryKey):
    """Get an case cost by its id."""
    case_cost = get(db_session=db_session, case_cost_id=case_cost_id)
    if not case_cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An case cost with this id does not exist."}],
        )
    return case_cost


@router.post(
    "",
    response_model=CaseCostRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_case_cost(db_session: DbSession, case_cost_in: CaseCostCreate):
    """Create an case cost."""
    case_cost = create(db_session=db_session, case_cost_in=case_cost_in)
    return case_cost


@router.put(
    "/{case_cost_id}",
    response_model=CaseCostRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_case_cost(
    db_session: DbSession,
    case_cost_id: PrimaryKey,
    case_cost_in: CaseCostUpdate,
):
    """Update an case cost by its id."""
    case_cost = get(db_session=db_session, case_cost_id=case_cost_id)
    if not case_cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An case cost with this id does not exist."}],
        )
    case_cost = update(
        db_session=db_session,
        case_cost=case_cost,
        case_cost_in=case_cost_in,
    )
    return case_cost


@router.delete(
    "/{case_cost_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_case_cost(db_session: DbSession, case_cost_id: PrimaryKey):
    """Delete an case cost, returning only an HTTP 200 OK if successful."""
    case_cost = get(db_session=db_session, case_cost_id=case_cost_id)
    if not case_cost:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An case cost with this id does not exist."}],
        )
    delete(db_session=db_session, case_cost_id=case_cost_id)
