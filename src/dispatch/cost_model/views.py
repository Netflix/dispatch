from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    CostModelCreate,
    CostModelPagination,
    CostModelRead,
    CostModelUpdate,
)
from .service import create, update, delete

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=CostModelPagination)
def get_cost_models(common: CommonParameters):
    """Get all s, or only those matching a given search term."""
    return search_filter_sort_paginate(model="CostModel", **common)


@router.post(
    "",
    summary="Creates a new .",
    response_model=CostModelRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_cost_model(
    db_session: DbSession,
    cost_model_in: CostModelCreate,
):
    """Create an ."""
    return create(db_session=db_session, cost_model_in=cost_model_in)


@router.put(
    "/{cost_model_id}",
    summary="Modifies an existing .",
    response_model=CostModelRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_cost_model(
    cost_model_id: PrimaryKey,
    db_session: DbSession,
    cost_model_in: CostModelUpdate,
):
    """Modifies an existing ."""
    return update(db_session=db_session, cost_model_in=cost_model_in)


@router.delete(
    "/{cost_model_id}",
    response_model=None,
    summary="Deletes an  and its activities.",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_cost_model(
    cost_model_id: PrimaryKey,
    db_session: DbSession,
):
    """Deletes an  and its external resources."""
    try:
        delete(cost_model_id=cost_model_id, db_session=db_session)
    except IntegrityError as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[
                {"msg": (f"Incident Cost Model with id {cost_model_id} could not be deleted. ")}
            ],
        ) from None
