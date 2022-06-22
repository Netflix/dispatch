import logging
from typing import List
from pydantic import Json

import json
import calendar
from datetime import date
from dateutil.relativedelta import relativedelta

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
from dispatch.common.utils.views import create_pydantic_include
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.case.enums import CaseStatus
from dispatch.individual.models import IndividualContactRead
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.participant.models import ParticipantUpdate

# NOTE: define flows before enabling code block
# from .flows import (
#     case_create_flow,
#     case_update_flow,
# )
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
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Create a new case."""
    if not case_in.reporter:
        case_in.reporter = ParticipantUpdate(
            individual=IndividualContactRead(email=current_user.email)
        )
    case = create(db_session=db_session, case_in=case_in)
    # NOTE: implement case flows before enabling line below
    # background_tasks.add_task(case_create_flow, case_id=case.id, organization_slug=organization)
    return case


@router.put(
    "/{case_id}",
    response_model=CaseRead,
    summary="Update an existing case.",
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
    # NOTE: implement case flows before enabling block below
    # background_tasks.add_task(
    #     case_update_flow,
    #     user_email=current_user.email,
    #     commander_email=case_in.commander.individual.email,
    #     reporter_email=case_in.reporter.individual.email,
    #     case_id=case_id,
    #     previous_case=previous_case,
    #     organization_slug=organization,
    # )

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
