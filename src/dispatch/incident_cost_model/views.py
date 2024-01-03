from fastapi import APIRouter, Depends, HTTPException, status
import logging
from starlette.requests import Request
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    IncidentCostModel,
    IncidentCostModelRead,
    IncidentCostModelCreate,
    IncidentCostModelUpdate,
    IncidentCostModelPagination,
)
from .service import create, update, delete, get_cost_model_by_id

log = logging.getLogger(__name__)

router = APIRouter()


def get_current_incident_cost_model(db_session: DbSession, request: Request) -> IncidentCostModel:
    """Fetches the current incident cost model or returns a 404."""
    incident_cost_model = get_cost_model_by_id(
        db_session=db_session, incident_cost_model_id=request.path_params["incident_cost_model_id"]
    )
    if not incident_cost_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An incident cost model with this id does not exist."}],
        )
    return incident_cost_model


CurrentIncidentCostModel = Annotated[IncidentCostModel, Depends(get_current_incident_cost_model)]


@router.get("", response_model=IncidentCostModelPagination)
def get_incident_cost_models(common: CommonParameters):
    """Get all incident cost models, or only those matching a given search term."""
    return search_filter_sort_paginate(model="IncidentCostModel", **common)


@router.post(
    "",
    summary="Creates a new incident cost model.",
    response_model=IncidentCostModelRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_incident_cost_model(
    db_session: DbSession,
    incident_cost_model_in: IncidentCostModelCreate,
):
    """Create an incident cost model."""
    return create(db_session=db_session, incident_cost_model_in=incident_cost_model_in)


@router.put(
    "/{incident_cost_model_id}",
    summary="Modifies an existing incident cost model.",
    response_model=IncidentCostModelRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_incident_cost_model(
    incident_cost_model_id: PrimaryKey,
    db_session: DbSession,
    incident_cost_model_in: IncidentCostModelUpdate,
):
    """Modifies an existing incident cost model."""
    return update(db_session=db_session, incident_cost_model_in=incident_cost_model_in)


@router.delete(
    "/{incident_cost_model_id}",
    response_model=None,
    summary="Deletes an incident cost model and its activities.",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_incident_cost_model(
    incident_cost_model_id: PrimaryKey,
    db_session: DbSession,
    current_incident_cost_model: CurrentIncidentCostModel,
):
    """Deletes an incident cost model and its external resources."""
    try:
        delete(incident_cost_model_id=current_incident_cost_model.id, db_session=db_session)
    except IntegrityError as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[
                {
                    "msg": (
                        f"Incident Cost Model {current_incident_cost_model.name} could not be deleted. "
                    )
                }
            ],
        ) from None
