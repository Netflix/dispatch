from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from .models import (
    TagTypeCreate,
    TagTypePagination,
    TagTypeRead,
    TagTypeUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=TagTypePagination)
def get_tag_types(*, common: dict = Depends(common_parameters)):
    """
    Get all tag types, or only those matching a given search term.
    """
    return search_filter_sort_paginate(model="TagType", **common)


@router.get("/{tag_type_id}", response_model=TagTypeRead)
def get_tag_type(*, db_session: Session = Depends(get_db), tag_type_id: str):
    """
    Get a tag type by its id.
    """
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(status_code=404, detail="A tag type with this id does not exist.")
    return tag_type


@router.post("", response_model=TagTypeRead)
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
