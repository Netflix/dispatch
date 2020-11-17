from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import (
    TagTypeCreate,
    TagTypePagination,
    TagTypeRead,
    TagTypeUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=TagTypePagination)
def get_tag_types(
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
    Get all tag types, or only those matching a given search term.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="TagType",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.get("/{tag_type_id}", response_model=TagTypeRead)
def get_tag_type(*, db_session: Session = Depends(get_db), tag_type_id: str):
    """
    Get a tag type by its id.
    """
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(status_code=404, detail="A tag type with this id does not exist.")
    return tag_type


@router.post("/", response_model=TagTypeRead)
def create_tag_type(*, db_session: Session = Depends(get_db), tag_type_in: TagTypeCreate):
    """
    Create a new tag type.
    """
    tag_type = create(db_session=db_session, tag_type_in=tag_type_in)
    return tag_type


@router.put("/{tag_type_id}", response_model=TagTypeRead)
def update_tag_type(
    *, db_session: Session = Depends(get_db), tag_type_id: int, tag_type_in: TagTypeUpdate
):
    """
    Update a tag type.
    """
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(status_code=404, detail="A tag type with this id does not exist.")
    tag_type = update(db_session=db_session, tag_type=tag_type, tag_type_in=tag_type_in)
    return tag_type


@router.delete("/{tag_type_id}")
def delete_tag_type(*, db_session: Session = Depends(get_db), tag_type_id: int):
    """
    Delete a tag type.
    """
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(status_code=404, detail="A tag type with this id does not exist.")
    delete(db_session=db_session, tag_type_id=tag_type_id)
