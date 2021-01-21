from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user

from dispatch.database import get_class_by_tablename, get_db, paginate
from dispatch.enums import SearchTypes, UserRoles

from dispatch.enums import Visibility

from .models import (
    SearchResponse,
    SearchFilter,
    SearchFilterCreate,
    SearchFilterUpdate,
    SearchFilterRead,
    SearchFilterPagination,
)
from .service import composite_search, create, delete, get, get_all, update

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


@router.get("/", response_model=SearchFilterPagination)
def get_filters(
    db_session: Session = Depends(get_db), page: int = 0, itemsPerPage: int = 5, q: str = None
):
    """
    Retrieve filters.
    """
    if q:
        query = search(db_session=db_session, query_str=q, model=SearchFilter)
    else:
        query = get_all(db_session=db_session)

    items, total = paginate(query=query, page=page, items_per_page=itemsPerPage)

    return {"items": items, "total": total}


@router.post("/", response_model=SearchFilterRead)
def create_search_filter(
    *, db_session: Session = Depends(get_db), search_filter_in: SearchFilterCreate
):
    """
    Create a new filter.
    """
    # TODO check for similarity
    search_filter = create(db_session=db_session, search_filter_in=search_filter_in)
    return search_filter


@router.put("/{search_filter_id}", response_model=SearchFilterRead)
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


@router.delete("/{search_filter_id}")
def delete_filter(*, db_session: Session = Depends(get_db), search_filter_id: int):
    """
    Delete a search filter.
    """
    search_filter = get(db_session=db_session, search_filter_id=search_filter_id)
    if not search_filter:
        raise HTTPException(status_code=404, detail="A search_filter with this id does not exist.")

    delete(db_session=db_session, search_filter_id=search_filter_id)
