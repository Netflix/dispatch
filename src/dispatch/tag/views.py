from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_class_by_tablename, get_db, search_filter_sort_paginate
from dispatch.tag.recommender import get_recommendations

from .models import (
    TagCreate,
    TagPagination,
    TagRead,
    TagUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TagPagination)
def get_tags(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
):
    """
    Get all tags, or only those matching a given search term.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Tag",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.get("/{tag_id}", response_model=TagRead)
def get_tag(*, db_session: Session = Depends(get_db), tag_id: str):
    """
    Given its unique ID, retrieve details about a single tag.
    """
    tag = get(db_session=db_session, tag_id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="The requested tag does not exist.")
    return tag


@router.post("/", response_model=TagRead)
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
