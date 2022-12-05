import calendar
import json
import logging

from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List

from starlette.requests import Request
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from dispatch.auth.permissions import (
    IncidentEditPermission,
    IncidentJoinOrSubscribePermission,
    IncidentViewPermission,
    PermissionsDependency,
)
from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.common.utils.views import create_pydantic_include
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.incident.enums import IncidentStatus
from dispatch.individual.models import IndividualContactRead
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.participant.models import ParticipantUpdate
from dispatch.report import flows as report_flows
from dispatch.report.models import TacticalReportCreate, ExecutiveReportCreate

from .flows import (
    incident_add_or_reactivate_participant_flow,
    incident_add_participant_to_tactical_group_flow,
    incident_create_closed_flow,
    incident_create_flow,
    incident_create_stable_flow,
    incident_update_flow,
)
from .metrics import make_forecast, create_incident_metric_query
from .models import Incident, IncidentCreate, IncidentPagination, IncidentRead, IncidentUpdate
from .service import create, delete, get, update


log = logging.getLogger(__name__)

router = APIRouter()


def get_current_incident(*, db_session: Session = Depends(get_db), request: Request) -> Incident:
    """Fetches incident or returns a 404."""
    incident = get(db_session=db_session, incident_id=request.path_params["incident_id"])
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident with this id does not existt."}],
        )
    return incident


@router.get("", summary="Retrieve a list of incidents.")
def get_incidents(
    *,
    common: dict = Depends(common_parameters),
    include: List[str] = Query([], alias="include[]"),
):
    """Retrieves a list of incidents."""
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
        return json.loads(IncidentPagination(**pagination).json(include=include_fields))
    return json.loads(IncidentPagination(**pagination).json())


@router.get(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Retrieves a single incident.",
    dependencies=[Depends(PermissionsDependency([IncidentViewPermission]))],
)
def get_incident(
    *,
    incident_id: PrimaryKey,
    db_session: Session = Depends(get_db),
    current_incident: Incident = Depends(get_current_incident),
):
    """Retrieves the details of a single incident."""
    return current_incident


@router.post("", response_model=IncidentRead, summary="Creates a new incident.")
def create_incident(
    *,
    db_session: Session = Depends(get_db),
    organization: OrganizationSlug,
    incident_in: IncidentCreate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Creates a new incident."""
    if not incident_in.reporter:
        incident_in.reporter = ParticipantUpdate(
            individual=IndividualContactRead(email=current_user.email)
        )
    incident = create(db_session=db_session, incident_in=incident_in)

    if incident.status == IncidentStatus.stable:
        background_tasks.add_task(
            incident_create_stable_flow, incident_id=incident.id, organization_slug=organization
        )
    elif incident.status == IncidentStatus.closed:
        background_tasks.add_task(
            incident_create_closed_flow, incident_id=incident.id, organization_slug=organization
        )
    else:
        background_tasks.add_task(
            incident_create_flow, incident_id=incident.id, organization_slug=organization
        )

    return incident


@router.put(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Updates an existing incident.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def update_incident(
    *,
    db_session: Session = Depends(get_db),
    current_incident: Incident = Depends(get_current_incident),
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    incident_in: IncidentUpdate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Updates an existing incident."""
    # we store the previous state of the incident in order to be able to detect changes
    previous_incident = IncidentRead.from_orm(current_incident)

    # we update the incident
    incident = update(db_session=db_session, incident=current_incident, incident_in=incident_in)

    # we run the incident update flow
    background_tasks.add_task(
        incident_update_flow,
        user_email=current_user.email,
        commander_email=incident_in.commander.individual.email,
        reporter_email=incident_in.reporter.individual.email,
        incident_id=incident_id,
        previous_incident=previous_incident,
        organization_slug=organization,
    )

    return incident


@router.post(
    "/{incident_id}/join",
    summary="Adds an individual to an incident.",
    dependencies=[Depends(PermissionsDependency([IncidentJoinOrSubscribePermission]))],
)
def join_incident(
    *,
    db_session: Session = Depends(get_db),
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: Incident = Depends(get_current_incident),
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Adds an individual to an incident."""
    background_tasks.add_task(
        incident_add_or_reactivate_participant_flow,
        current_user.email,
        incident_id=current_incident.id,
        organization_slug=organization,
    )


@router.post(
    "/{incident_id}/subscribe",
    summary="Subscribes an individual to an incident.",
    dependencies=[Depends(PermissionsDependency([IncidentJoinOrSubscribePermission]))],
)
def subscribe_to_incident(
    *,
    db_session: Session = Depends(get_db),
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: Incident = Depends(get_current_incident),
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Subscribes an individual to an incident."""
    background_tasks.add_task(
        incident_add_participant_to_tactical_group_flow,
        current_user.email,
        incident_id=current_incident.id,
        organization_slug=organization,
    )


@router.post(
    "/{incident_id}/report/tactical",
    summary="Creates a tactical report.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def create_tactical_report(
    *,
    db_session: Session = Depends(get_db),
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    tactical_report_in: TacticalReportCreate,
    current_user: DispatchUser = Depends(get_current_user),
    current_incident: Incident = Depends(get_current_incident),
    background_tasks: BackgroundTasks,
):
    """Creates a tactical report."""
    background_tasks.add_task(
        report_flows.create_tactical_report,
        user_email=current_user.email,
        incident_id=current_incident.id,
        tactical_report_in=tactical_report_in,
        organization_slug=organization,
    )


@router.post(
    "/{incident_id}/report/executive",
    summary="Creates an executive report.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def create_executive_report(
    *,
    db_session: Session = Depends(get_db),
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: Incident = Depends(get_current_incident),
    executive_report_in: ExecutiveReportCreate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """Creates an executive report."""
    background_tasks.add_task(
        report_flows.create_executive_report,
        user_email=current_user.email,
        incident_id=current_incident.id,
        executive_report_in=executive_report_in,
        organization_slug=organization,
    )


@router.delete(
    "/{incident_id}",
    response_model=None,
    summary="Delete an incident.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def delete_incident(
    *,
    incident_id: PrimaryKey,
    db_session: Session = Depends(get_db),
    current_incident: Incident = Depends(get_current_incident),
):
    """Deletes an incident."""
    delete(db_session=db_session, incident_id=current_incident.id)


def get_month_range(relative):
    today = date.today()
    relative_month = today - relativedelta(months=relative)
    _, month_end_day = calendar.monthrange(relative_month.year, relative_month.month)
    month_start = relative_month.replace(day=1)
    month_end = relative_month.replace(day=month_end_day)
    return month_start, month_end


@router.get("/metric/forecast", summary="Gets incident forecast data.")
def get_incident_forecast(
    *,
    db_session: Session = Depends(get_db),
    common: dict = Depends(common_parameters),
):
    """Gets incident forecast data."""
    categories = []
    predicted = []
    actual = []

    for i in reversed(range(1, 5)):
        start_date, end_date = get_month_range(i)

        if i == 1:
            incidents = create_incident_metric_query(
                db_session=db_session,
                filter_spec=common["filter_spec"],
                end_date=end_date,
            )
            predicted_months, predicted_counts = make_forecast(incidents=incidents)
            categories = categories + predicted_months
            predicted = predicted + predicted_counts

        else:
            incidents = create_incident_metric_query(
                db_session=db_session, filter_spec=common["filter_spec"], end_date=end_date
            )

            # get only first predicted month for completed months
            predicted_months, predicted_counts = make_forecast(incidents=incidents)
            if predicted_months and predicted_counts:
                categories.append(predicted_months[0])
                predicted.append(predicted_counts[0])

        # get actual month counts
        incidents = create_incident_metric_query(
            db_session=db_session,
            filter_spec=common["filter_spec"],
            end_date=end_date,
            start_date=start_date,
        )

        actual.append(len(incidents))

    if not (len(predicted)):
        return {
            "categories": categories,
            "series": [
                {"name": "Predicted", "data": []},
                {"name": "Actual", "data": []},
            ],
        }

    return {
        "categories": categories,
        "series": [
            {"name": "Predicted", "data": predicted},
            {"name": "Actual", "data": actual[1:]},
        ],
    }
