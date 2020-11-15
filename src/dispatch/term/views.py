from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import TermCreate, TermPagination, TermRead, TermUpdate
from .service import create, delete, get, get_by_text, update

router = APIRouter()


@router.get("/", response_model=TermPagination)
def get_terms(
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
    Retrieve all terms.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Term",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.post("/", response_model=TermRead)
def create_term(*, db_session: Session = Depends(get_db), term_in: TermCreate):
    """
    Create a new term.
    """
    term = get_by_text(db_session=db_session, text=term_in.text)
    if term:
        raise HTTPException(
            status_code=400, detail=f"The term with this text ({term_in.text}) already exists."
        )
    term = create(db_session=db_session, term_in=term_in)
    return term


@router.get("/{term_id}", response_model=TermRead)
def get_term(*, db_session: Session = Depends(get_db), term_id: int):
    """
    Update a term.
    """
    term = get(db_session=db_session, term_id=term_id)
    if not term:
        raise HTTPException(status_code=404, detail="The term with this id does not exist.")
    return term


@router.put("/{term_id}", response_model=TermRead)
def update_term(*, db_session: Session = Depends(get_db), term_id: int, term_in: TermUpdate):
    """
    Update a term.
    """
    term = get(db_session=db_session, term_id=term_id)
    if not term:
        raise HTTPException(status_code=404, detail="The term with this id does not exist.")
    term = update(db_session=db_session, term=term, term_in=term_in)
    return term


@router.delete("/{term_id}", response_model=TermRead)
def delete_term(*, db_session: Session = Depends(get_db), term_id: int):
    """
    Update a term.
    """
    term = get(db_session=db_session, term_id=term_id)
    if not term:
        raise HTTPException(status_code=404, detail="The term with this id does not exist.")
    return delete(db_session=db_session, term_id=term_id)
