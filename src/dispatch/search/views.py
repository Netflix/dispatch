from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.database.core import get_db, get_class_by_tablename
from dispatch.database.service import search_filter_sort_paginate
from dispatch.enums import SearchTypes, UserRoles
from dispatch.enums import Visibility

from .models import (
    SearchResponse,
    SearchFilterCreate,
    SearchFilterUpdate,
    SearchFilterRead,
    SearchFilterPagination,
)
from .service import composite_search, create, delete, get, update

router = APIRouter()


@router.get("/", response_class=JSONResponse)
def search(
    *,
    db_session: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    q: str = None,
    type: List[str] = [
        v.value for v in SearchTypes
    ],  # hack for pydantic enum json generation see: https://github.com/samuelcolvin/pydantic/pull/1749
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Perform a search.
    """
    if q:
        models = [get_class_by_tablename(t) for t in type]
        results = composite_search(db_session=db_session, query_str=q, models=models)
    else:
        results = []

    # add a filter for restricted incidents
    if current_user.role != UserRoles.admin:
        results["Incident"] = [i for i in results["Incident"] if i.visibility == Visibility.open]

    return SearchResponse(**{"query": q, "results": results}).dict(by_alias=False)


@router.get("/filters", response_model=SearchFilterPagination)
def get_filters(
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
    Retrieve filters.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="SearchFilter",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


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
