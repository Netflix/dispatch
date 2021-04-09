from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.database.core import get_db, get_class_by_tablename
from dispatch.database.service import composite_search
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.enums import SearchTypes, UserRoles
from dispatch.enums import Visibility

from .models import (
    SearchResponse,
    SearchFilterCreate,
    SearchFilterUpdate,
    SearchFilterRead,
    SearchFilterPagination,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_class=JSONResponse)
def search(
    *,
    common: dict = Depends(common_parameters),
    type: List[str] = [
        v.value for v in SearchTypes
    ],  # hack for pydantic enum json generation see: https://github.com/samuelcolvin/pydantic/pull/1749
):
    """
    Perform a search.
    """
    if common["query_str"]:
        models = [get_class_by_tablename(t) for t in type]
        results = composite_search(
            db_session=common["db_session"],
            query_str=common["query_str"],
            models=models,
            current_user=common["current_user"],
        )
    else:
        results = []

    # add a filter for restricted incidents
    # TODO won't currently show incidents that you are a member
    admin_projects = []
    for p in common["current_user"].projects:
        if p.role == UserRoles.admin:
            admin_projects.append(p)

    filtered_incidents = []
    for incident in results["Incident"]:
        if incident.project in admin_projects:
            filtered_incidents.append(incident)
            continue

        if incident.visibility == Visibility.open:
            filtered_incidents.append(incident)

    results["Incident"] = filtered_incidents

    return SearchResponse(**{"query": common["query_str"], "results": results}).dict(by_alias=False)


@router.get("/filters", response_model=SearchFilterPagination)
def get_filters(*, common: dict = Depends(common_parameters)):
    """
    Retrieve filters.
    """
    return search_filter_sort_paginate(model="SearchFilter", **common)


@router.post("/filters", response_model=SearchFilterRead)
def create_search_filter(
    *, db_session: Session = Depends(get_db), search_filter_in: SearchFilterCreate
):
    """
    Create a new filter.
    """
    try:
        search_filter = create(db_session=db_session, search_filter_in=search_filter_in)
        return search_filter
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="A search filter already exists with this name."
        )


@router.put("/filters/{search_filter_id}", response_model=SearchFilterRead)
def update_search_filter(
    *,
    db_session: Session = Depends(get_db),
    search_filter_id: int,
    search_filter_in: SearchFilterUpdate,
):
    """
    Update a search filter.
    """
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(status_code=404, detail="A search_filter with this id does not exist.")
    search_filter = update(
        db_session=db_session, search_filter=search_filter, search_filter_in=search_filter_in
    )
    return search_filter


@router.delete("/filters/{search_filter_id}")
def delete_filter(*, db_session: Session = Depends(get_db), search_filter_id: int):
    """
    Delete a search filter.
    """
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(status_code=404, detail="A search_filter with this id does not exist.")

    delete(db_session=db_session, search_filter_id=search_filter_id)
