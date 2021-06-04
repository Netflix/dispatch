import json
from typing import List

import calendar
from datetime import date
from dateutil.relativedelta import relativedelta

from starlette.requests import Request
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from dispatch.auth.permissions import (
    IncidentEditPermission,
    IncidentJoinPermission,
    PermissionsDependency,
    IncidentViewPermission,
)

from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.common.utils.views import create_pydantic_include
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.incident.enums import IncidentStatus
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.report import flows as report_flows
from dispatch.report.models import TacticalReportCreate, ExecutiveReportCreate

from .flows import (
    incident_add_or_reactivate_participant_flow,
    incident_assign_role_flow,
    incident_create_closed_flow,
    incident_create_flow,
    incident_create_stable_flow,
    incident_update_flow,
)
from .metrics import make_forecast, create_incident_metric_query
from .models import Incident, IncidentCreate, IncidentPagination, IncidentRead, IncidentUpdate
from .service import create, delete, get, update


router = APIRouter()


def get_current_incident(*, db_session: Session = Depends(get_db), request: Request) -> Incident:
    """Fetches incident or returns a 404."""
    incident = get(db_session=db_session, incident_id=request.path_params["incident_id"])
    if not incident:
        raise HTTPException(status_code=404, detail="The requested incident does not exist.")
    return incident


@router.get("", summary="Retrieve a list of all incidents.")
def get_incidents(
    *,
    common: dict = Depends(common_parameters),
    include: List[str] = Query([], alias="include[]"),
):
    """
    Retrieve a list of all incidents.
    """
    pagination = search_filter_sort_paginate(model="Incident", **common)

    if include:
        # only allow two levels for now
        include_sets = create_pydantic_include(include)

        include_fields = {
            "items": {"__all__": include_sets},
            "itemsPerPage": ...,
            "page": ...,
            "total": ...,
        }
        return IncidentPagination(**pagination).dict(include=include_fields)
    return IncidentPagination(**pagination).dict()


@router.get(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Retrieve a single incident.",
    dependencies=[Depends(PermissionsDependency([IncidentViewPermission]))],
)
def get_incident(
    *,
    db_session: Session = Depends(get_db),
    current_incident: Incident = Depends(get_current_incident),
):
    """
    Retrieve details about a specific incident.
    """
    return current_incident


@router.post("", response_model=IncidentRead, summary="Create a new incident.")
def create_incident(
    *,
    db_session: Session = Depends(get_db),
    incident_in: IncidentCreate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """
    Create a new incident.
    """
    try:
        incident = create(
            db_session=db_session, reporter_email=current_user.email, **incident_in.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if incident.status == IncidentStatus.stable.value:
        background_tasks.add_task(incident_create_stable_flow, incident_id=incident.id)
    elif incident.status == IncidentStatus.closed.value:
        background_tasks.add_task(incident_create_closed_flow, incident_id=incident.id)
    else:
        background_tasks.add_task(incident_create_flow, incident_id=incident.id)

    return incident


@router.put(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Update an existing incident.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def update_incident(
    *,
    db_session: Session = Depends(get_db),
    current_incident: Incident = Depends(get_current_incident),
    incident_in: IncidentUpdate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """
    Update an individual incident.
    """
    previous_incident = IncidentRead.from_orm(current_incident)

    # NOTE: Order matters we have to get the previous state for change detection
    try:
        incident = update(db_session=db_session, incident=current_incident, incident_in=incident_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    background_tasks.add_task(
        incident_update_flow,
        user_email=current_user.email,
        incident_id=incident.id,
        previous_incident=previous_incident,
    )

    # assign commander
    background_tasks.add_task(
        incident_assign_role_flow,
        current_user.email,
        incident_id=incident.id,
        assignee_email=incident_in.commander.individual.email,
        assignee_role=ParticipantRoleType.incident_commander.value,
    )

    # assign reporter
    background_tasks.add_task(
        incident_assign_role_flow,
        current_user.email,
        incident_id=incident.id,
        assignee_email=incident_in.reporter.individual.email,
        assignee_role=ParticipantRoleType.reporter.value,
    )

    return incident


@router.post(
    "/{incident_id}/join",
    summary="Join an incident.",
    dependencies=[Depends(PermissionsDependency([IncidentJoinPermission]))],
)
def join_incident(
    *,
    db_session: Session = Depends(get_db),
    current_incident: Incident = Depends(get_current_incident),
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """
    Join an individual incident.
    """
    background_tasks.add_task(
        incident_add_or_reactivate_participant_flow,
        current_user.email,
        incident_id=current_incident.id,
    )


@router.post(
    "/{incident_id}/report/tactical",
    summary="Create a tactical report.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def create_tactical_report(
    *,
    db_session: Session = Depends(get_db),
    tactical_report_in: TacticalReportCreate,
    current_user: DispatchUser = Depends(get_current_user),
    current_incident: Incident = Depends(get_current_incident),
    background_tasks: BackgroundTasks,
):
    """
    Creates a new tactical report.
    """
    background_tasks.add_task(
        report_flows.create_tactical_report,
        user_email=current_user.email,
        incident_id=current_incident.id,
        tactical_report_in=tactical_report_in,
    )


@router.post(
    "/{incident_id}/report/executive",
    summary="Create an executive report.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def create_executive_report(
    *,
    db_session: Session = Depends(get_db),
    current_incident: Incident = Depends(get_current_incident),
    executive_report_in: ExecutiveReportCreate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """
    Creates a new executive report.
    """
    background_tasks.add_task(
        report_flows.create_executive_report,
        user_email=current_user.email,
        incident_id=current_incident.id,
        executive_report_in=executive_report_in,
    )


@router.delete(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Delete an incident.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def delete_incident(
    *,
    db_session: Session = Depends(get_db),
    current_incident: Incident = Depends(get_current_incident),
):
    """
    Delete an individual incident.
    """
    delete(db_session=db_session, incident_id=current_incident.id)


def get_month_range(relative):
    today = date.today()
    relative_month = today - relativedelta(months=relative)
    _, month_end_day = calendar.monthrange(relative_month.year, relative_month.month)
    month_start = relative_month.replace(day=1)
    month_end = relative_month.replace(day=month_end_day)
    return month_start, month_end


@router.get("/metric/forecast", summary="Get incident forecast data.")
def get_incident_forecast(
    *,
    db_session: Session = Depends(get_db),
    filter_spec: str = Query(None, alias="filter"),
):
    """
    Get incident forecast data.
    """
    categories = []
    predicted = []
    actual = []

    if filter_spec:
        filter_spec = json.loads(filter_spec)

    for i in reversed(range(1, 5)):
        start_date, end_date = get_month_range(i)

        if i == 1:
            incidents = create_incident_metric_query(
                db_session=db_session,
                filter_spec=filter_spec,
                end_date=end_date,
            )

            predicted_months, predicted_counts = make_forecast(incidents=incidents)
            categories = categories + predicted_months
            predicted = predicted + predicted_counts

        else:
            incidents = create_incident_metric_query(
                db_session=db_session, filter_spec=filter_spec, end_date=end_date
            )

            # get only first predicted month for completed months
            predicted_months, predicted_counts = make_forecast(incidents=incidents)
            if predicted_months and predicted_counts:
                categories.append(predicted_months[0])
                predicted.append(predicted_counts[0])

        # get actual month counts
        incidents = create_incident_metric_query(
            db_session=db_session, filter_spec=filter_spec, end_date=end_date, start_date=start_date
        )

        actual.append(len(incidents))

    return {
        "categories": categories,
        "series": [
            {"name": "Predicted", "data": predicted},
            {"name": "Actual", "data": actual[1:]},
        ],
    }
