from fastapi import APIRouter, HTTPException, status

from dispatch.ai import service as ai_service
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    TagCreate,
    TagPagination,
    TagRead,
    TagRecommendationResponse,
    TagUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=TagPagination)
def get_tags(common: CommonParameters):
    """Get all tags, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Tag", **common)


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(db_session: DbSession, tag_id: PrimaryKey):
    """Given its unique id, retrieve details about a single tag."""
    tag = get(db_session=db_session, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The requested tag does not exist."}],
        )
    return tag


@router.post("", response_model=TagRead)
def create_tag(db_session: DbSession, tag_in: TagCreate):
    """Creates a new tag."""
    return create(db_session=db_session, tag_in=tag_in)


@router.put("/{tag_id}", response_model=TagRead)
def update_tag(db_session: DbSession, tag_id: PrimaryKey, tag_in: TagUpdate):
    """Updates an existing tag."""
    tag = get(db_session=db_session, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A tag with this id does not exist."}],
        )
    return update(db_session=db_session, tag=tag, tag_in=tag_in)


@router.delete("/{tag_id}", response_model=None)
def delete_tag(db_session: DbSession, tag_id: PrimaryKey):
    """Deletes a tag, returning only an HTTP 200 OK if successful."""
    tag = get(db_session=db_session, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A tag with this id does not exist."}],
        )
    delete(db_session=db_session, tag_id=tag_id)


@router.get(
    "/recommendations/{project_id}/case/{case_id}", response_model=TagRecommendationResponse
)
def get_tag_recommendations_case(db_session: DbSession, project_id: int, case_id: int):
    """Retrieves a tag recommendation based on the model and model id."""
    return ai_service.get_tag_recommendations(
        db_session=db_session, project_id=project_id, case_id=case_id
    )


@router.get(
    "/recommendations/{project_id}/incident/{incident_id}", response_model=TagRecommendationResponse
)
def get_tag_recommendations_incident(db_session: DbSession, project_id: int, incident_id: int):
    """Retrieves a tag recommendation based on the model and model id."""
    return ai_service.get_tag_recommendations(
        db_session=db_session, project_id=project_id, incident_id=incident_id
    )
