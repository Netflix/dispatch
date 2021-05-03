from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db, get_class_by_tablename
from dispatch.database.service import common_parameters, search_filter_sort_paginate
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
def get_tags(*, common: dict = Depends(common_parameters)):
    """
    Get all tags, or only those matching a given search term.
    """
    return search_filter_sort_paginate(model="Tag", **common)


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(*, db_session: Session = Depends(get_db), tag_id: str):
    """
    Given its unique ID, retrieve details about a single tag.
    """
    tag = get(db_session=db_session, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="The requested tag does not exist.")
    return tag


@router.post("", response_model=TagRead)
def create_tag(*, db_session: Session = Depends(get_db), tag_in: TagCreate):
    """
    Create a new tag.
    """
    tag = create(db_session=db_session, tag_in=tag_in)
    return tag


@router.put("/{tag_id}", response_model=TagRead)
def update_tag(*, db_session: Session = Depends(get_db), tag_id: int, tag_in: TagUpdate):
    """
    Given its unique ID, update details of an tag.
    """
    tag = get(db_session=db_session, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="An tag with this ID does not exist.")
    tag = update(db_session=db_session, tag=tag, tag_in=tag_in)
    return tag


@router.delete("/{tag_id}")
def delete_tag(*, db_session: Session = Depends(get_db), tag_id: int):
    """
    Delete an tag, returning only an HTTP 200 OK if successful.
    """
    tag = get(db_session=db_session, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="An tag with this ID does not exist.")
    delete(db_session=db_session, tag_id=tag_id)


@router.get("/recommendations/{model_name}/{id}", response_model=TagPagination)
def get_tag_recommendations(*, db_session: Session = Depends(get_db), model_name: str, id: int):
    """
    Retrieves a tag recommendation based on the model and model id.
    """
    model_object = get_class_by_tablename(model_name)
    model = db_session.query(model_object).filter(model_object.id == id).one_or_none()

    if not model:
        raise HTTPException(
            status_code=404, detail=f"No model found. ModelName: {model_name} Id: {id}"
        )

    tags = get_recommendations(db_session, [t.id for t in model.tags], model_name)
    return {"items": tags, "total": len(tags)}
