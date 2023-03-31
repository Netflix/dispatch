from fastapi import APIRouter, Depends, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    CasePriorityCreate,
    CasePriorityPagination,
    CasePriorityRead,
    CasePriorityUpdate,
)
from .service import create, get, update


router = APIRouter()


@router.get("", response_model=CasePriorityPagination, tags=["case_priorities"])
def get_case_priorities(common: CommonParameters):
    """Returns all case priorities."""
    return search_filter_sort_paginate(model="CasePriority", **common)


@router.post(
    "",
    response_model=CasePriorityRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_case_priority(
    db_session: DbSession,
    case_priority_in: CasePriorityCreate,
):
    """Creates a new case priority."""
    case_priority = create(db_session=db_session, case_priority_in=case_priority_in)
    return case_priority


@router.put(
    "/{case_priority_id}",
    response_model=CasePriorityRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_case_priority(
    *,
    db_session: DbSession,
    case_priority_id: PrimaryKey,
    case_priority_in: CasePriorityUpdate,
):
    """Updates an existing case priority."""
    case_priority = get(db_session=db_session, case_priority_id=case_priority_id)
    if not case_priority:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A case priority with this id does not exist."}],
        )

    case_priority = update(
        db_session=db_session,
        case_priority=case_priority,
        case_priority_in=case_priority_in,
    )
    return case_priority


@router.get("/{case_priority_id}", response_model=CasePriorityRead)
def get_case_priority(db_session: DbSession, case_priority_id: PrimaryKey):
    """Gets a case priority."""
    case_priority = get(db_session=db_session, case_priority_id=case_priority_id)
    if not case_priority:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A case priority with this id does not exist."}],
        )
    return case_priority
