import logging
from typing import List

import json
from datetime import date

from starlette.requests import Request
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

# NOTE: define permissions before enabling the code block below
# from dispatch.auth.permissions import (
#     CaseEditPermission,
#     CaseJoinPermission,
#     PermissionsDependency,
#     CaseViewPermission,
# )
from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.case.enums import CaseStatus
from dispatch.common.utils.views import create_pydantic_include
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import OrganizationSlug, PrimaryKey

from .flows import (
    case_closed_create_flow,
    case_escalated_create_flow,
    case_new_create_flow,
    case_triage_create_flow,
    case_update_flow,
)
from .models import Case, CaseCreate, CasePagination, CaseRead, CaseUpdate
from .service import create, delete, get, update


log = logging.getLogger(__name__)

router = APIRouter()


def get_current_case(*, db_session: Session = Depends(get_db), request: Request) -> Case:
    """Fetches case or returns an HTTP 404."""
    case = get(db_session=db_session, case_id=request.path_params["case_id"])
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested case does not exist."}],
        )
    return case


@router.get("", summary="Retrieve a list of all cases.")
def get_cases(
    *,
    common: dict = Depends(common_parameters),
    include: List[str] = Query([], alias="include[]"),
):
    """Retrieve a list of all cases."""
    pagination = search_filter_sort_paginate(model="Case", **common)

    if include:
        # only allow two levels for now
        include_sets = create_pydantic_include(include)

        include_fields = {
            "items": {"__all__": include_sets},
            "itemsPerPage": ...,
            "page": ...,
            "total": ...,
        }
        return json.loads(CasePagination(**pagination).json(include=include_fields))
    return json.loads(CasePagination(**pagination).json())


@router.post("", response_model=CaseRead, summary="Create a new case.")
def create_case(
    *,
    db_session: Session = Depends(get_db),
    organization: OrganizationSlug,
    case_in: CaseCreate,
    # current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Creates a new case."""
    case = create(db_session=db_session, case_in=case_in)

    if case.status == CaseStatus.triage:
        background_tasks.add_task(
            case_triage_create_flow,
            case_id=case.id,
            organization_slug=organization,
        )
    elif case.status == CaseStatus.escalated:
        background_tasks.add_task(
            case_escalated_create_flow,
            case_id=case.id,
            organization_slug=organization,
        )
    elif case.status == CaseStatus.closed:
        background_tasks.add_task(
            case_closed_create_flow,
            case_id=case.id,
            organization_slug=organization,
        )
    else:
        background_tasks.add_task(
            case_new_create_flow,
            case_id=case.id,
            organization_slug=organization,
        )

    # if result["status_code"] != status.HTTP_201_CREATED:
    #     raise HTTPException(
    #         status_code=result["status_code"],
    #         detail=[result["msg"]],
    #     )

    return case


@router.put(
    "/{case_id}",
    response_model=CaseRead,
    summary="Updates an existing case.",
    # dependencies=[Depends(PermissionsDependency([CaseEditPermission]))],
)
def update_case(
    *,
    db_session: Session = Depends(get_db),
    current_case: Case = Depends(get_current_case),
    organization: OrganizationSlug,
    case_id: PrimaryKey,
    case_in: CaseUpdate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Update an existing case."""
    # we store the previous state of the case in order to be able to detect changes
    previous_case = CaseRead.from_orm(current_case)

    # we update the case
    case = update(db_session=db_session, case=current_case, case_in=case_in)

    # we run the case update flow
    background_tasks.add_task(
        case_update_flow,
        case_id=case_id,
        previous_case=previous_case,
        user_email=current_user.email,
        organization_slug=organization,
    )

    return case


@router.delete(
    "/{case_id}",
    response_model=CaseRead,
    summary="Delete an case.",
    # dependencies=[Depends(PermissionsDependency([CaseEditPermission]))],
)
def delete_case(
    *,
    case_id: PrimaryKey,
    db_session: Session = Depends(get_db),
    current_case: Case = Depends(get_current_case),
):
    """Delete an individual case."""
    delete(db_session=db_session, case_id=current_case.id)
