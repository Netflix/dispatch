from fastapi import APIRouter, HTTPException, status

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


@router.get("/recommendations/{project_id}", response_model=TagRecommendationResponse)
def get_tag_recommendations(db_session: DbSession, project_id: int):
    """Retrieves a tag recommendation based on the model and model id."""
    recommendations = [
        {
            "tag_type_id": 135,
            "tags": [
                {
                    "id": 58019,
                    "name": "Reconnaissance",
                    "reason": (
                        "The attacker could use the unauthenticated API to gather "
                        "information about users by mapping phone numbers to email addresses."
                    ),
                },
                {
                    "id": 58020,
                    "name": "Collection",
                    "reason": (
                        "The ability to automate the extraction of email addresses by "
                        "inputting phone numbers suggests a tactic focused on collecting "
                        "sensitive data."
                    ),
                },
                {
                    "id": 58021,
                    "name": "Impact",
                    "reason": (
                        "The exposure of email addresses linked to phone numbers can lead "
                        "to privacy violations or facilitate further attacks like phishing."
                    ),
                },
            ],
        },
        {
            "tag_type_id": 136,
            "tags": [
                {
                    "id": 58022,
                    "name": "Active Scanning",
                    "reason": (
                        "This technique involves actively probing a target to gather "
                        "information and identify vulnerabilities, which aligns with how "
                        "an attacker might exploit the unauthenticated API."
                    ),
                },
                {
                    "id": 58023,
                    "name": "Gather Victim Identity Information",
                    "reason": (
                        "This technique encompasses collecting information about victims, "
                        "such as email addresses and phone numbers, which is relevant given "
                        "the incident's focus on extracting email addresses using phone numbers."
                    ),
                },
                {
                    "id": 58024,
                    "name": "Data from Cloud Storage",
                    "reason": (
                        "While not a perfect fit, this technique involves accessing data "
                        "from cloud storage, relating to accessing user data stored or "
                        "exposed through online services, such as the unauthenticated API."
                    ),
                },
            ],
        },
    ]

    return {"recommendations": recommendations}
