import logging
from typing import List

import json

from starlette.requests import Request
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# NOTE: define permissions before enabling the code block below
from dispatch.auth.permissions import (
    CaseEditPermission,
    # CaseJoinPermission,
    PermissionsDependency,
    CaseViewPermission,
)
from dispatch.auth import service as auth_service
from dispatch.auth.models import DispatchUser
from dispatch.case.enums import CaseStatus
from dispatch.common.utils.views import create_pydantic_include
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.incident.models import IncidentCreate, IncidentRead
from dispatch.incident import service as incident_service
from dispatch.participant.models import ParticipantUpdate
from dispatch.individual.models import IndividualContactRead

from .flows import (
    case_closed_create_flow,
    case_delete_flow,
    case_escalated_create_flow,
    case_to_incident_endpoint_escalate_flow,
    case_new_create_flow,
    case_triage_create_flow,
    case_update_flow,
)
from .models import Case, CaseCreate, CasePagination, CaseRead, CaseUpdate
from .service import create, delete, get, update


log = logging.getLogger(__name__)

router = APIRouter()


def get_current_case(*, db_session: Session = Depends(get_db), request: Request) -> Case:
    """Fetches a case or returns an HTTP 404."""
    case = get(db_session=db_session, case_id=request.path_params["case_id"])
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested case does not exist."}],
        )
    return case


@router.get(
    "/{case_id}",
    response_model=CaseRead,
    summary="Retrieves a single case.",
    dependencies=[Depends(PermissionsDependency([CaseViewPermission]))],
)
def get_case(
    *,
    case_id: PrimaryKey,
    db_session: Session = Depends(get_db),
    current_case: Case = Depends(get_current_case),
):
    """Retrieves the details of a single case."""
    return current_case


@router.get("", summary="Retrieves a list of cases.")
def get_cases(
    *,
    common: dict = Depends(common_parameters),
    include: List[str] = Query([], alias="include[]"),
):
    """Retrieves all cases."""
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


@router.post("", response_model=CaseRead, summary="Creates a new case.")
def create_case(
    *,
    db_session: Session = Depends(get_db),
    organization: OrganizationSlug,
    case_in: CaseCreate,
    current_user: DispatchUser = Depends(auth_service.get_current_user),
    background_tasks: BackgroundTasks,
):
    """Creates a new case."""
    # TODO: (wshel) this conditional always happens in the UI flow since
    # reporter is not available to be set.
    if not case_in.reporter:
        case_in.reporter = ParticipantUpdate(
            individual=IndividualContactRead(email=current_user.email)
        )
    case = create(db_session=db_session, case_in=case_in, current_user=current_user)

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

    return case


@router.put(
    "/{case_id}",
    response_model=CaseRead,
    summary="Updates an existing case.",
    dependencies=[Depends(PermissionsDependency([CaseEditPermission]))],
)
def update_case(
    *,
    db_session: Session = Depends(get_db),
    current_case: Case = Depends(get_current_case),
    organization: OrganizationSlug,
    case_id: PrimaryKey,
    case_in: CaseUpdate,
    current_user: DispatchUser = Depends(auth_service.get_current_user),
    background_tasks: BackgroundTasks,
):
    """Updates an existing case."""
    # we store the previous state of the case in order to be able to detect changes
    previous_case = CaseRead.from_orm(current_case)

    # we update the case
    case = update(
        db_session=db_session, case=current_case, case_in=case_in, current_user=current_user
    )

    # we run the case update flow
    background_tasks.add_task(
        case_update_flow,
        case_id=case_id,
        previous_case=previous_case,
        assignee_email=case_in.assignee.individual.email,
        user_email=current_user.email,
        organization_slug=organization,
    )

    return case


@router.put(
    "/{case_id}/escalate",
    response_model=IncidentRead,
    summary="Escalates an existing case.",
    dependencies=[Depends(PermissionsDependency([CaseEditPermission]))],
)
def escalate_case(
    *,
    db_session: Session = Depends(get_db),
    current_case: Case = Depends(get_current_case),
    organization: OrganizationSlug,
    incident_in: IncidentCreate,
    current_user: DispatchUser = Depends(auth_service.get_current_user),
    background_tasks: BackgroundTasks,
):
    """Escalates an existing case."""
    # current user is better than assignee (although likely the same)
    if not incident_in.reporter:
        incident_in.reporter = ParticipantUpdate(
            individual=IndividualContactRead(email=current_user.email)
        )

    # allow for default values
    if not incident_in.incident_type:
        if current_case.case_type.incident_type:
            incident_in.incident_type = {"name": current_case.case_type.incident_type.name}

    if not incident_in.project:
        if current_case.case_type.incident_type:
            incident_in.project = {"name": current_case.case_type.incident_type.project.name}

    incident = incident_service.create(db_session=db_session, incident_in=incident_in)
    background_tasks.add_task(
        case_to_incident_endpoint_escalate_flow,
        case_id=current_case.id,
        incident_id=incident.id,
        organization_slug=organization,
    )

    return incident


@router.delete(
    "/{case_id}",
    response_model=None,
    summary="Deletes an existing case and its external resources.",
    dependencies=[Depends(PermissionsDependency([CaseEditPermission]))],
)
def delete_case(
    *,
    case_id: PrimaryKey,
    db_session: Session = Depends(get_db),
    current_case: Case = Depends(get_current_case),
):
    """Deletes an existing case and its external resources."""
    # we run the case delete flow
    case_delete_flow(case=current_case, db_session=db_session)

    # we delete the internal case
    try:
        delete(db_session=db_session, case_id=case_id)
    except IntegrityError as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[
                {
                    "msg": (
                        f"Case {current_case.name} could not be deleted. Make sure the case has no "
                        "relationships to other cases or incidents before deleting it.",
                    )
                }
            ],
        ) from None
