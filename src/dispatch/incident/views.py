from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.database import get_db, search_filter_sort_paginate
from dispatch.enums import Visibility, UserRoles
from dispatch.incident.enums import IncidentStatus
from dispatch.participant_role.models import ParticipantRoleType

from .flows import (
    incident_add_or_reactivate_participant_flow,
    incident_assign_role_flow,
    incident_create_closed_flow,
    incident_create_flow,
    incident_create_stable_flow,
    incident_update_flow,
)
from .metrics import make_forecast
from .models import IncidentCreate, IncidentPagination, IncidentRead, IncidentUpdate
from .service import create, delete, get, update


router = APIRouter()


@router.get("/", response_model=IncidentPagination, summary="Retrieve a list of all incidents.")
def get_incidents(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Retrieve a list of all incidents.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Incident",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
        join_attrs=[
            ("tag", "tags"),
        ],
        user_role=current_user.role,
    )


@router.get("/{incident_id}", response_model=IncidentRead, summary="Retrieve a single incident.")
def get_incident(
    *,
    db_session: Session = Depends(get_db),
    incident_id: str,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Retrieve details about a specific incident.
    """
    incident = get(db_session=db_session, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="The requested incident does not exist.")

    # we want to provide additional protections around restricted incidents
    if incident.visibility == Visibility.restricted:
        # reject if the user isn't an admin, reporter or commander
        if incident.reporter.email == current_user.email:
            return incident

        if incident.commander.email == current_user.email:
            return incident

        if current_user.role == UserRoles.admin:
            return incident

        raise HTTPException(
            status_code=401, detail="You do no have permission to view this incident."
        )

    return incident


@router.post("/", response_model=IncidentRead, summary="Create a new incident.")
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
    incident = create(
        db_session=db_session, reporter_email=current_user.email, **incident_in.dict()
    )

    if incident.status == IncidentStatus.stable:
        background_tasks.add_task(incident_create_stable_flow, incident_id=incident.id)
    elif incident.status == IncidentStatus.closed:
        background_tasks.add_task(incident_create_closed_flow, incident_id=incident.id)
    else:
        background_tasks.add_task(incident_create_flow, incident_id=incident.id)

    return incident


@router.put("/{incident_id}", response_model=IncidentRead, summary="Update an existing incident.")
def update_incident(
    *,
    db_session: Session = Depends(get_db),
    incident_id: str,
    incident_in: IncidentUpdate,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """
    Update an individual incident.
    """
    incident = get(db_session=db_session, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="The requested incident does not exist.")

    # we want to provide additional protections around restricted incidents
    if incident.visibility == Visibility.restricted:
        # reject if the user isn't an admin or commander
        if current_user.email != incident.commander.email or current_user.role != UserRoles.admin:
            raise HTTPException(
                status_code=401, detail="You do no have permission to update this incident."
            )

    previous_incident = IncidentRead.from_orm(incident)

    # NOTE: Order matters we have to get the previous state for change detection
    incident = update(db_session=db_session, incident=incident, incident_in=incident_in)

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
        assignee_email=incident_in.commander.email,
        assignee_role=ParticipantRoleType.incident_commander,
    )

    # assign reporter
    background_tasks.add_task(
        incident_assign_role_flow,
        current_user.email,
        incident_id=incident.id,
        assignee_email=incident_in.reporter.email,
        assignee_role=ParticipantRoleType.reporter,
    )

    return incident


@router.post("/{incident_id}/join", summary="Join an incident.")
def join_incident(
    *,
    db_session: Session = Depends(get_db),
    incident_id: str,
    current_user: DispatchUser = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """
    Join an individual incident.
    """
    incident = get(db_session=db_session, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="The requested incident does not exist.")

    # we want to provide additional protections around restricted incidents
    if incident.visibility == Visibility.restricted:
        # reject if the user isn't an admin
        if current_user.role != UserRoles.admin.value:
            raise HTTPException(
                status_code=401, detail="You do no have permission to join this incident."
            )

    background_tasks.add_task(
        incident_add_or_reactivate_participant_flow, current_user.email, incident_id=incident.id
    )


@router.delete("/{incident_id}", response_model=IncidentRead, summary="Delete an incident.")
def delete_incident(*, db_session: Session = Depends(get_db), incident_id: str):
    """
    Delete an individual incident.
    """
    incident = get(db_session=db_session, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="The requested incident does not exist.")
    delete(db_session=db_session, incident_id=incident.id)


@router.get("/metric/forecast/{incident_type}", summary="Get incident forecast data.")
def get_incident_forecast(*, db_session: Session = Depends(get_db), incident_type: str):
    """
    Get incident forecast data.
    """
    return make_forecast(db_session=db_session, incident_type=incident_type)
