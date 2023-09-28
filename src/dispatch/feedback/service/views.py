from fastapi import APIRouter

from dispatch.database.service import search_filter_sort_paginate, CommonParameters

from .models import ServiceFeedbackPagination


router = APIRouter()


@router.get("", response_model=ServiceFeedbackPagination)
def get_feedback_entries(commons: CommonParameters):
    """Get all feedback entries, or only those matching a given search term."""
    return search_filter_sort_paginate(model="ServiceFeedback", **commons)
