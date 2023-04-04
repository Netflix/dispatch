from fastapi import APIRouter, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
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
def get_queries(common: CommonParameters):
    """Get all queries, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Query", **common)


@router.get("/{query_id}", response_model=QueryRead)
def get_query(db_session: DbSession, query_id: PrimaryKey):
    """Given its unique ID, retrieve details about a single query."""
    query = get(db_session=db_session, query_id=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested query does not exist."}],
        )
    return query


@router.post("", response_model=QueryRead)
def create_query(db_session: DbSession, query_in: QueryCreate):
    """Creates a new data query."""
    return create(db_session=db_session, query_in=query_in)


@router.put("/{query_id}", response_model=QueryRead)
def update_query(db_session: DbSession, query_id: PrimaryKey, query_in: QueryUpdate):
    """Updates a data query."""
    query = get(db_session=db_session, query_id=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A data query with this id does not exist."}],
        )
    return update(db_session=db_session, query=query, query_in=query_in)


@router.delete("/{query_id}", response_model=None)
def delete_query(db_session: DbSession, query_id: PrimaryKey):
    """Deletes a data query, returning only an HTTP 200 OK if successful."""
    query = get(db_session=db_session, query_id=query_id)
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A data query with this id does not exist."}],
        )
    delete(db_session=db_session, query_id=query_id)
