from fastapi import APIRouter, Depends, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    CaseSeverityCreate,
    CaseSeverityPagination,
    CaseSeverityRead,
    CaseSeverityUpdate,
)
from .service import create, get, update


router = APIRouter()


@router.get("", response_model=CaseSeverityPagination, tags=["case_severities"])
def get_case_severities(common: CommonParameters):
    """Returns all case severities."""
    return search_filter_sort_paginate(model="CaseSeverity", **common)


@router.post(
    "",
    response_model=CaseSeverityRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_case_severity(
    *,
    db_session: DbSession,
    case_severity_in: CaseSeverityCreate,
):
    """Creates a new case severity."""
    case_severity = create(db_session=db_session, case_severity_in=case_severity_in)
    return case_severity


@router.put(
    "/{case_severity_id}",
    response_model=CaseSeverityRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_case_severity(
    *,
    db_session: DbSession,
    case_severity_id: PrimaryKey,
    case_severity_in: CaseSeverityUpdate,
):
    """Updates an existing case severity."""
    case_severity = get(db_session=db_session, case_severity_id=case_severity_id)
    if not case_severity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A case severity with this id does not exist."}],
        )

    case_severity = update(
        db_session=db_session,
        case_severity=case_severity,
        case_severity_in=case_severity_in,
    )
    return case_severity


@router.get("/{case_severity_id}", response_model=CaseSeverityRead)
def get_case_severity(db_session: DbSession, case_severity_id: PrimaryKey):
    """Gets a case severity."""
    case_severity = get(db_session=db_session, case_severity_id=case_severity_id)
    if not case_severity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A case severity with this id does not exist."}],
        )
    return case_severity
