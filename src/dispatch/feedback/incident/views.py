from fastapi import APIRouter, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import search_filter_sort_paginate, CommonParameters
from dispatch.models import PrimaryKey


from .models import (
    FeedbackCreate,
    FeedbackPagination,
    FeedbackRead,
    FeedbackUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=FeedbackPagination)
def get_feedback_entries(commons: CommonParameters):
    """Get all feedback entries, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Feedback", **commons)


@router.get("/{feedback_id}", response_model=FeedbackRead)
def get_feedback(db_session: DbSession, feedback_id: PrimaryKey):
    """Get a feedback entry by its id."""
    feedback = get(db_session=db_session, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A feedback entry with this id does not exist."}],
        )
    return feedback


@router.post("", response_model=FeedbackRead)
def create_feedback(db_session: DbSession, feedback_in: FeedbackCreate):
    """Create a new feedback entry."""
    return create(db_session=db_session, feedback_in=feedback_in)


@router.put("/{feedback_id}", response_model=FeedbackRead)
def update_feedback(db_session: DbSession, feedback_id: PrimaryKey, feedback_in: FeedbackUpdate):
    """Updates a feeback entry by its id."""
    feedback = get(db_session=db_session, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A feedback entry with this id does not exist."}],
        )
    feedback = update(db_session=db_session, feedback=feedback, feedback_in=feedback_in)
    return feedback


@router.delete("/{feedback_id}", response_model=None)
def delete_feedback(db_session: DbSession, feedback_id: PrimaryKey):
    """Delete a feedback entry, returning only an HTTP 200 OK if successful."""
    feedback = get(db_session=db_session, feedback_id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A feedback entry with this id does not exist."}],
        )
    delete(db_session=db_session, feedback_id=feedback_id)
