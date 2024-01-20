import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
import json
import logging
from typing import Annotated, List
from starlette.requests import Request
from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import (
    IncidentEditPermission,
    IncidentCommanderOrScribePermission,
    IncidentJoinOrSubscribePermission,
    IncidentViewPermission,
    PermissionsDependency,
)
from dispatch.auth.service import CurrentUser
from dispatch.common.utils.views import create_pydantic_include
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.event import flows as event_flows
from dispatch.event.models import EventUpdate, EventCreateMinimal
from dispatch.incident.enums import IncidentStatus
from dispatch.individual.models import IndividualContactRead
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.participant.models import ParticipantUpdate
from dispatch.report import flows as report_flows
from dispatch.report.models import ExecutiveReportCreate, TacticalReportCreate

from .flows import (
    incident_add_or_reactivate_participant_flow,
    incident_create_closed_flow,
    incident_create_flow,
    incident_create_stable_flow,
    incident_delete_flow,
    incident_subscribe_participant_flow,
    incident_update_flow,
    incident_create_resources_flow,
)
from .metrics import create_incident_metric_query, make_forecast
from .models import (
    Incident,
    IncidentCreate,
    IncidentExpandedPagination,
    IncidentPagination,
    IncidentRead,
    IncidentUpdate,
)
from .service import create, delete, get, update

log = logging.getLogger(__name__)

router = APIRouter()


def get_current_incident(db_session: DbSession, request: Request) -> Incident:
    """Fetches incident or returns a 404."""
    incident = get(db_session=db_session, incident_id=request.path_params["incident_id"])
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident with this id does not exist."}],
        )
    return incident


CurrentIncident = Annotated[Incident, Depends(get_current_incident)]


@router.get("", summary="Retrieve a list of incidents.")
def get_incidents(
    common: CommonParameters,
    include: List[str] = Query([], alias="include[]"),
    expand: bool = Query(default=False),
):
    """Retrieves a list of incidents."""
    pagination = search_filter_sort_paginate(model="Incident", **common)

    if expand:
        return json.loads(IncidentExpandedPagination(**pagination).json())

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
    incident_id: PrimaryKey,
    db_session: DbSession,
    current_incident: CurrentIncident,
):
    """Retrieves the details of a single incident."""
    return current_incident


@router.post("", response_model=IncidentRead, summary="Creates a new incident.")
def create_incident(
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_in: IncidentCreate,
    current_user: CurrentUser,
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


@router.post(
    "/{incident_id}/resources",
    response_model=IncidentRead,
    summary="Creates resources for an existing incident.",
)
def create_incident_resources(
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: CurrentIncident,
    background_tasks: BackgroundTasks,
):
    """Creates resources for an existing incident."""
    background_tasks.add_task(
        incident_create_resources_flow, organization_slug=organization, incident_id=incident_id
    )

    return current_incident


@router.put(
    "/{incident_id}",
    response_model=IncidentRead,
    summary="Updates an existing incident.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def update_incident(
    db_session: DbSession,
    current_incident: CurrentIncident,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    incident_in: IncidentUpdate,
    current_user: CurrentUser,
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


@router.delete(
    "/{incident_id}",
    response_model=None,
    summary="Deletes an incident and its external resources.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def delete_incident(
    incident_id: PrimaryKey,
    db_session: DbSession,
    current_incident: CurrentIncident,
):
    """Deletes an incident and its external resources."""
    # we run the incident delete flow
    incident_delete_flow(incident=current_incident, db_session=db_session)

    # we delete the internal incident
    try:
        delete(incident_id=current_incident.id, db_session=db_session)
    except IntegrityError as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[
                {
                    "msg": (
                        f"Incident {current_incident.name} could not be deleted. Make sure the incident has no "
                        "relationships to other incidents or cases before deleting it.",
                    )
                }
            ],
        ) from None


@router.post(
    "/{incident_id}/join",
    summary="Adds an individual to an incident.",
    dependencies=[Depends(PermissionsDependency([IncidentJoinOrSubscribePermission]))],
)
def join_incident(
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: CurrentIncident,
    current_user: CurrentUser,
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
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: CurrentIncident,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
):
    """Subscribes an individual to an incident."""
    background_tasks.add_task(
        incident_subscribe_participant_flow,
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
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    tactical_report_in: TacticalReportCreate,
    current_user: CurrentUser,
    current_incident: CurrentIncident,
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
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: CurrentIncident,
    executive_report_in: ExecutiveReportCreate,
    current_user: CurrentUser,
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


@router.post(
    "/{incident_id}/event",
    summary="Creates a custom event.",
    dependencies=[Depends(PermissionsDependency([IncidentEditPermission]))],
)
def create_custom_event(
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: CurrentIncident,
    event_in: EventCreateMinimal,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
):
    event_in.details.update({"created_by": current_user.email, "added_on": str(datetime.utcnow())})
    """Creates a custom event."""
    background_tasks.add_task(
        event_flows.log_incident_event,
        user_email=current_user.email,
        incident_id=current_incident.id,
        event_in=event_in,
        organization_slug=organization,
    )


@router.patch(
    "/{incident_id}/event",
    summary="Updates a custom event.",
    dependencies=[Depends(PermissionsDependency([IncidentCommanderOrScribePermission]))],
)
def update_custom_event(
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: CurrentIncident,
    event_in: EventUpdate,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
):
    if event_in.details:
        event_in.details.update(
            {
                **event_in.details,
                "updated_by": current_user.email,
                "updated_on": str(datetime.utcnow()),
            }
        )
    else:
        event_in.details = {"updated_by": current_user.email, "updated_on": str(datetime.utcnow())}
    """Updates a custom event."""
    background_tasks.add_task(
        event_flows.update_incident_event,
        event_in=event_in,
        organization_slug=organization,
    )


@router.post(
    "/{incident_id}/exportTimeline",
    summary="Exports timeline events.",
    dependencies=[Depends(PermissionsDependency([IncidentCommanderOrScribePermission]))],
)
def export_timeline_event(
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: CurrentIncident,
    timeline_filters: dict,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
):
    result = background_tasks.add_task(
        event_flows.export_timeline,
        timeline_filters=timeline_filters,
        incident_id=incident_id,
        organization_slug=organization,
    )
    return result


@router.delete(
    "/{incident_id}/event/{event_uuid}",
    summary="Deletes a custom event.",
    dependencies=[Depends(PermissionsDependency([IncidentCommanderOrScribePermission]))],
)
def delete_custom_event(
    db_session: DbSession,
    organization: OrganizationSlug,
    incident_id: PrimaryKey,
    current_incident: CurrentIncident,
    event_uuid: str,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
):
    """Deletes a custom event."""
    background_tasks.add_task(
        event_flows.delete_incident_event,
        event_uuid=event_uuid,
        organization_slug=organization,
    )


def get_month_range(relative):
    today = date.today()
    relative_month = today - relativedelta(months=relative)
    _, month_end_day = calendar.monthrange(relative_month.year, relative_month.month)
    month_start = relative_month.replace(day=1)
    month_end = relative_month.replace(day=month_end_day)
    return month_start, month_end


@router.get("/metric/forecast", summary="Gets incident forecast data.")
def get_incident_forecast(
    db_session: DbSession,
    common: CommonParameters,
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
