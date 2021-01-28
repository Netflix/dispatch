from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.database import get_db, search_filter_sort_paginate
from dispatch.enums import UserRoles

from .models import (
    IncidentPriorityCreate,
    IncidentPriorityPagination,
    IncidentPriorityRead,
    IncidentPriorityUpdate,
)
from .service import create, get, update


router = APIRouter()


@router.get("/", response_model=IncidentPriorityPagination, tags=["incident_priorities"])
def get_incident_priorities(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="field[]"),
    ops: List[str] = Query([], alias="op[]"),
    values: List[str] = Query([], alias="value[]"),
):
    """
    Returns all incident priorities.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="IncidentPriority",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.post("/", response_model=IncidentPriorityRead)
def create_incident_priority(
    *,
    db_session: Session = Depends(get_db),
    incident_priority_in: IncidentPriorityCreate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Create a new incident priority.
    """
    # We restrict the creation of incident priorities to admins only
    if current_user.role != UserRoles.admin:
        raise HTTPException(
            status_code=403, detail="You do not have permission to create incident priorities."
        )
    incident_priority = create(db_session=db_session, incident_priority_in=incident_priority_in)
    return incident_priority


@router.put("/{incident_priority_id}", response_model=IncidentPriorityRead)
def update_incident_priority(
    *,
    db_session: Session = Depends(get_db),
    incident_priority_id: int,
    incident_priority_in: IncidentPriorityUpdate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Update an existing incident priority.
    """
    incident_priority = get(db_session=db_session, incident_priority_id=incident_priority_id)
    if not incident_priority:
        raise HTTPException(
            status_code=404, detail="The incident priority with this id does not exist."
        )

    # We restrict updating incident priorities to admins only
    if current_user.role != UserRoles.admin:
        raise HTTPException(
            status_code=403, detail="You do not have permission to update incident priorities."
        )

    incident_priority = update(
        db_session=db_session,
        incident_priority=incident_priority,
        incident_priority_in=incident_priority_in,
    )
    return incident_priority


@router.get("/{incident_priority_id}", response_model=IncidentPriorityRead)
def get_incident_priority(*, db_session: Session = Depends(get_db), incident_priority_id: int):
    """
    Get an incident priority.
    """
    incident_priority = get(db_session=db_session, incident_priority_id=incident_priority_id)
    if not incident_priority:
        raise HTTPException(
            status_code=404, detail="The incident priority with this id does not exist."
        )
    return incident_priority
