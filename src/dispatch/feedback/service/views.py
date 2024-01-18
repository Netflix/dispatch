from fastapi import APIRouter, HTTPException, status, Depends

from dispatch.auth.permissions import (
    FeedbackDeletePermission,
    PermissionsDependency,
    SensitiveProjectActionPermission,
)
from dispatch.database.core import DbSession
from dispatch.database.service import search_filter_sort_paginate, CommonParameters
from dispatch.models import PrimaryKey

from .models import ServiceFeedbackRead, ServiceFeedbackPagination
from .service import get, delete


router = APIRouter()


@router.get(
    "",
    response_model=ServiceFeedbackPagination,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def get_feedback_entries(commons: CommonParameters):
    """Get all feedback entries, or only those matching a given search term."""
    return search_filter_sort_paginate(model="ServiceFeedback", **commons)


@router.get(
    "/{service_feedback_id}",
    response_model=ServiceFeedbackRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def get_feedback(db_session: DbSession, service_feedback_id: PrimaryKey):
    """Get a feedback entry by its id."""
    feedback = get(db_session=db_session, service_feedback_id=service_feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A feedback entry with this id does not exist."}],
        )
    return feedback


@router.delete(
    "/{service_feedback_id}/{individual_contact_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([FeedbackDeletePermission]))],
)
def delete_feedback(db_session: DbSession, service_feedback_id: PrimaryKey):
    """Delete a feedback entry, returning only an HTTP 200 OK if successful."""
    feedback = get(db_session=db_session, service_feedback_id=service_feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A feedback entry with this id does not exist."}],
        )
    delete(db_session=db_session, service_feedback_id=service_feedback_id)
