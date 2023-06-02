from fastapi import APIRouter, HTTPException, status

from dispatch.database.core import DbSession, get_class_by_tablename
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey
from dispatch.tag.recommender import get_recommendations

from .models import (
    TagCreate,
    TagPagination,
    TagRead,
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
    """Updates an exisiting tag."""
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


@router.get("/recommendations/{model_name}/{id}", response_model=TagPagination)
def get_tag_recommendations(db_session: DbSession, model_name: str, id: int):
    """Retrieves a tag recommendation based on the model and model id."""
    model_object = get_class_by_tablename(model_name)
    model = db_session.query(model_object).filter(model_object.id == id).one_or_none()
    project_slug = model.project.slug
    organization_slug = model.project.organization.slug

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": f"No model with id {id} and name {model_name} found."}],
        )

    tags = get_recommendations(
        db_session, [t.id for t in model.tags], organization_slug, project_slug, model_name
    )
    return {"items": tags, "total": len(tags)}
