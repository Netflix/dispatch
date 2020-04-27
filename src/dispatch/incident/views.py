from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi_permissions import has_permission
from sqlalchemy.orm import Session

from dispatch.enums import Visibility
from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.database import get_db, search_filter_sort_paginate

from dispatch.participant_role.models import ParticipantRoleType

from dispatch.auth.models import UserRoles
from .flows import incident_create_flow, incident_update_flow, incident_assign_role_flow
from .models import IncidentCreate, IncidentPagination, IncidentRead, IncidentUpdate
from .service import create, delete, get, update
from .metrics import make_forecast

router = APIRouter()


@router.get("/", response_model=IncidentPagination, summary="Retrieve a list of all incidents.")
def get_incidents(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query(None, alias="sortBy[]"),
    descending: List[bool] = Query(None, alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Retrieve a list of all incidents.
    """
    # we want to provide additional protections around restricted incidents
    # Because we want to proactively filter (instead of when the item is returned
    # we don't use fastapi_permissions acls.
    if current_user.role != UserRoles.admin:
        # add a filter for restricted incidents
        fields.append("visibility")
        values.append(Visibility.restricted)
        ops.append("!=")

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
        join_attrs=[("tag", "tags")],
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
    if not has_permission(current_user.principals, "view", IncidentRead.__acl__):
        raise HTTPException(
            status_code=401, detail="You do no have permission to view this incident."
        )

    return incident


@router.post("/", response_model=IncidentRead, summary="Create a new incident.")
def create_incident(
    *,
    db_session: Session = Depends(get_db),
    incident_in: IncidentCreate,
    current_user_email: str = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """
    Create a new incident.
    """
    incident = create(
        db_session=db_session, reporter_email=current_user_email, **incident_in.dict()
    )

    background_tasks.add_task(incident_create_flow, incident_id=incident.id)

    return incident


@router.put("/{incident_id}", response_model=IncidentRead, summary="Update an existing incident.")
def update_incident(
    *,
    db_session: Session = Depends(get_db),
    incident_id: str,
    incident_in: IncidentUpdate,
    current_user_email: str = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    """
    Update an individual incident.
    """
    incident = get(db_session=db_session, incident_id=incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="The requested incident does not exist.")

    previous_incident = IncidentRead.from_orm(incident)

    # NOTE: Order matters we have to get the previous state for change detection
    incident = update(db_session=db_session, incident=incident, incident_in=incident_in)

    background_tasks.add_task(
        incident_update_flow,
        user_email=current_user_email,
        incident_id=incident.id,
        previous_incident=previous_incident,
    )

    # assign commander
    background_tasks.add_task(
        incident_assign_role_flow,
        current_user_email,
        incident_id=incident.id,
        assignee_email=incident_in.commander.email,
        assignee_role=ParticipantRoleType.incident_commander,
    )

    # assign reporter
    background_tasks.add_task(
        incident_assign_role_flow,
        current_user_email,
        incident_id=incident.id,
        assignee_email=incident_in.reporter.email,
        assignee_role=ParticipantRoleType.reporter,
    )

    return incident


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
