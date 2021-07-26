from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

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
    """Get all tag types, or only those matching a given search term."""
    return search_filter_sort_paginate(model="TagType", **common)


@router.get("/{tag_type_id}", response_model=TagTypeRead)
def get_tag_type(*, db_session: Session = Depends(get_db), tag_type_id: PrimaryKey):
    """Get a tag type by its id."""
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A tag type with this id does not exist."}],
        )
    return tag_type


@router.post("", response_model=TagTypeRead)
def create_tag_type(*, db_session: Session = Depends(get_db), tag_type_in: TagTypeCreate):
    """Create a new tag type."""
    try:
        tag_type = create(db_session=db_session, tag_type_in=tag_type_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "An tag type with this name already exists.",
                    "loc": ["name"],
                    "type": "Exists",
                }
            ],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": str(e),
                    "loc": ["Unknown"],
                    "type": "Unknown",
                }
            ],
        )

    return tag_type


@router.put("/{tag_type_id}", response_model=TagTypeRead)
def update_tag_type(
    *, db_session: Session = Depends(get_db), tag_type_id: PrimaryKey, tag_type_in: TagTypeUpdate
):
    """Update a tag type."""
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A tag type with this id does not exist."}],
        )

    try:
        tag_type = update(db_session=db_session, tag_type=tag_type, tag_type_in=tag_type_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "An tag type with this name already exists.",
                    "loc": ["name"],
                    "type": "Exists",
                }
            ],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": str(e),
                    "loc": ["Unknown"],
                    "type": "Unknown",
                }
            ],
        )

    return tag_type


@router.delete("/{tag_type_id}")
def delete_tag_type(*, db_session: Session = Depends(get_db), tag_type_id: PrimaryKey):
    """Delete a tag type."""
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A tag type with this id does not exist."}],
        )
    delete(db_session=db_session, tag_type_id=tag_type_id)
