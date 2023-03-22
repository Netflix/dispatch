from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    WorkstreamTypeCreate,
    WorkstreamTypePagination,
    WorkstreamTypeRead,
    WorkstreamTypeUpdate,
)
from .service import create, get, update


router = APIRouter()


@router.get("/{workstream_type_id}", response_model=WorkstreamTypeRead)
def get_workstream_type(*, db_session: Session = Depends(get_db), workstream_type_id: PrimaryKey):
    """Gets a workstream type."""
    workstream_type = get(db_session=db_session, workstream_type_id=workstream_type_id)
    if not workstream_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workstream type with this id does not exist."}],
        )
    return workstream_type


@router.get("", response_model=WorkstreamTypePagination, tags=["workstream_types"])
def get_workstream_types(*, common: dict = Depends(common_parameters)):
    """Returns all workstream types."""
    return search_filter_sort_paginate(model="WorkstreamType", **common)


@router.post(
    "",
    response_model=WorkstreamTypeRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_workstream_type(
    *,
    db_session: Session = Depends(get_db),
    workstream_type_in: WorkstreamTypeCreate,
):
    """Creates a new workstream type."""
    return create(db_session=db_session, workstream_type_in=workstream_type_in)


@router.put(
    "/{workstream_type_id}",
    response_model=WorkstreamTypeRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_workstream_type(
    *,
    db_session: Session = Depends(get_db),
    workstream_type_id: PrimaryKey,
    workstream_type_in: WorkstreamTypeUpdate,
):
    """Updates an existing workstream type."""
    workstream_type = get(db_session=db_session, workstream_type_id=workstream_type_id)
    if not workstream_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workstream type with this id does not exist."}],
        )
    return update(
        db_session=db_session,
        workstream_type=workstream_type,
        workstream_type_in=workstream_type_in,
    )
