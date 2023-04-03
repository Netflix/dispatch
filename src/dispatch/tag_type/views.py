from fastapi import APIRouter, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.exc import IntegrityError

from dispatch.database.core import DbSession
from dispatch.exceptions import ExistsError
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
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
def get_tag_types(common: CommonParameters):
    """Get all tag types, or only those matching a given search term."""
    return search_filter_sort_paginate(model="TagType", **common)


@router.get("/{tag_type_id}", response_model=TagTypeRead)
def get_tag_type(db_session: DbSession, tag_type_id: PrimaryKey):
    """Get a tag type by its id."""
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A tag type with this id does not exist."}],
        )
    return tag_type


@router.post("", response_model=TagTypeRead)
def create_tag_type(db_session: DbSession, tag_type_in: TagTypeCreate):
    """Create a new tag type."""
    try:
        tag_type = create(db_session=db_session, tag_type_in=tag_type_in)
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A tag type with this name already exists."), loc="name"
                )
            ],
            model=TagTypeCreate,
        ) from None
    return tag_type


@router.put("/{tag_type_id}", response_model=TagTypeRead)
def update_tag_type(db_session: DbSession, tag_type_id: PrimaryKey, tag_type_in: TagTypeUpdate):
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
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A tag type with this name already exists."), loc="name"
                )
            ],
            model=TagTypeUpdate,
        ) from None
    return tag_type


@router.delete("/{tag_type_id}", response_model=None)
def delete_tag_type(db_session: DbSession, tag_type_id: PrimaryKey):
    """Delete a tag type."""
    tag_type = get(db_session=db_session, tag_type_id=tag_type_id)
    if not tag_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A tag type with this id does not exist."}],
        )
    delete(db_session=db_session, tag_type_id=tag_type_id)
