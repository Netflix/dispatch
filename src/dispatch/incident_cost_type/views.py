from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.auth.permissions import AdminPermission, PermissionsDependency
from dispatch.database.core import get_db
from dispatch.database.service import search_filter_sort_paginate

from .models import (
    IncidentCostTypeCreate,
    IncidentCostTypePagination,
    IncidentCostTypeRead,
    IncidentCostTypeUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("/", response_model=IncidentCostTypePagination)
def get_incident_cost_types(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
):
    """
    Get all incident cost types, or only those matching a given search term.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="IncidentCostType",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.get("/{incident_cost_type_id}", response_model=IncidentCostTypeRead)
def get_incident_cost_type(*, db_session: Session = Depends(get_db), incident_cost_type_id: int):
    """
    Get an incident cost type by id.
    """
    incident_cost_type = get(db_session=db_session, incident_cost_type_id=incident_cost_type_id)
    if not incident_cost_type:
        raise HTTPException(
            status_code=404, detail="An incident cost type with this id does not exist."
        )
    return incident_cost_type


@router.post("/", response_model=IncidentCostTypeRead)
def create_incident_cost_type(
    *, db_session: Session = Depends(get_db), incident_cost_type_in: IncidentCostTypeCreate
):
    """
    Create an incident cost type.
    """
    incident_cost_type = create(db_session=db_session, incident_cost_type_in=incident_cost_type_in)
    return incident_cost_type


@router.put("/{incident_cost_type_id}", response_model=IncidentCostTypeRead)
def update_incident_cost_type(
    *,
    db_session: Session = Depends(get_db),
    incident_cost_type_id: int,
    incident_cost_type_in: IncidentCostTypeUpdate,
):
    """
    Update an incident cost type by id.
    """
    incident_cost_type = get(db_session=db_session, incident_cost_type_id=incident_cost_type_id)
    if not incident_cost_type:
        raise HTTPException(
            status_code=404, detail="An incident cost type with this id does not exist."
        )

    if not incident_cost_type.editable:
        raise HTTPException(
            status_code=301, detail="You are not allowed to update this incident cost type."
        )

    incident_cost_type = update(
        db_session=db_session,
        incident_cost_type=incident_cost_type,
        incident_cost_type_in=incident_cost_type_in,
    )
    return incident_cost_type


@router.delete("/{incident_cost_type_id}")
def delete_incident_cost_type(*, db_session: Session = Depends(get_db), incident_cost_type_id: int):
    """
    Delete an incident cost type, returning only an HTTP 200 OK if successful.
    """
    incident_cost_type = get(db_session=db_session, incident_cost_type_id=incident_cost_type_id)

    if not incident_cost_type:
        raise HTTPException(
            status_code=404, detail="An incident cost type with this id does not exist."
        )

    if not incident_cost_type.editable:
        raise HTTPException(
            status_code=301, detail="You are not allowed to delete this incident cost type."
        )

    delete(db_session=db_session, incident_cost_type_id=incident_cost_type_id)
