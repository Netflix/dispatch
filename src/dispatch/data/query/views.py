from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    QueryCreate,
    QueryPagination,
    QueryRead,
    QueryUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=QueryPagination)
def get_queries(*, common: dict = Depends(common_parameters)):
    """Get all queries, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Query", **common)


@router.get("/{query_id}", response_model=QueryRead)
def get_query(*, db_session: Session = Depends(get_db), query_id: PrimaryKey):
    """Given its unique ID, retrieve details about a single query."""
    query = get(db_session=db_session, query_id=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested query does not exist."}],
        )
    return query


@router.post("", response_model=QueryRead)
def create_query(*, db_session: Session = Depends(get_db), query_in: QueryCreate):
    """Create a new query."""
    query = create(db_session=db_session, query_in=query_in)
    return query


@router.put("/{query_id}", response_model=QueryRead)
def update_query(
    *, db_session: Session = Depends(get_db), query_id: PrimaryKey, query_in: QueryUpdate
):
    """Update a query."""
    query = get(db_session=db_session, query_id=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A query with this ID does not exist."}],
        )
    query = update(db_session=db_session, query=query, query_in=query_in)
    return query


@router.delete("/{query_id}")
def delete_query(*, db_session: Session = Depends(get_db), query_id: PrimaryKey):
    """Delete a query, returning only an HTTP 200 OK if successful."""
    query = get(db_session=db_session, query_id=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A query with this ID does not exist."}],
        )
    delete(db_session=db_session, query_id=query_id)
