from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import (
    FeedbackCreate,
    FeedbackPagination,
    FeedbackRead,
    FeedbackUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("/", response_model=FeedbackPagination)
def get_feedback_entries(
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
    Get all feedback entries, or only those matching a given search term.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Feedback",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.get("/{feedback_id}", response_model=FeedbackRead)
def get_feedback(*, db_session: Session = Depends(get_db), feedback_id: int):
    """
    Get a feedback entry by its id.
    """
    feedback = get(db_session=db_session, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="A feedback entry with this id does not exist.")
    return feedback


@router.post("/", response_model=FeedbackRead)
def create_feedback(*, db_session: Session = Depends(get_db), feedback_in: FeedbackCreate):
    """
    Create a new feedback entry.
    """
    feedback = create(db_session=db_session, feedback_in=feedback_in)
    return feedback


@router.put("/{feedback_id}", response_model=FeedbackRead)
def update_feedback(
    *, db_session: Session = Depends(get_db), feedback_id: int, feedback_in: FeedbackUpdate
):
    """
    Updates a feeback entry by its id.
    """
    feedback = get(db_session=db_session, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="A feedback entry with this id does not exist.")
    feedback = update(db_session=db_session, feedback=feedback, feedback_in=feedback_in)
    return feedback


@router.delete("/{feedback_id}")
def delete_feedback(*, db_session: Session = Depends(get_db), feedback_id: int):
    """
    Delete a feedback entry, returning only an HTTP 200 OK if successful.
    """
    feedback = get(db_session=db_session, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="A feedback entry with this id does not exist.")
    delete(db_session=db_session, feedback_id=feedback_id)
