from fastapi import APIRouter, HTTPException, status, Depends

from dispatch.auth.permissions import (
    SensitiveProjectActionPermission,
    PermissionsDependency,
)
from dispatch.database.core import DbSession
from dispatch.database.service import search_filter_sort_paginate, CommonParameters
from dispatch.models import PrimaryKey

from .models import FormsTypeRead, FormsTypePagination
from .service import get, delete


router = APIRouter()


@router.get("", response_model=FormsTypePagination)
def get_forms(commons: CommonParameters):
    """Get all form types, or only those matching a given search term."""
    return search_filter_sort_paginate(model="FormsType", **commons)


@router.get("/{forms_type_id}", response_model=FormsTypeRead)
def get_form(db_session: DbSession, forms_type_id: PrimaryKey):
    """Get a form type by its id."""
    forms_type = get(db_session=db_session, forms_type_id=forms_type_id)
    if not forms_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form type with this id does not exist."}],
        )
    return forms_type


@router.delete(
    "/{forms_type_id}",
    response_model=None,
    dependencies=[
        Depends(PermissionsDependency([SensitiveProjectActionPermission]))
    ],
)
def delete_form(db_session: DbSession, forms_type_id: PrimaryKey):
    """Delete a form type, returning only an HTTP 200 OK if successful."""
    forms_type = get(db_session=db_session, forms_type_id=forms_type_id)
    if not forms_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A form type with this id does not exist."}],
        )
    delete(db_session=db_session, forms_type_id=forms_type_id)
