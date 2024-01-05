from fastapi import APIRouter, Depends, HTTPException, status
import logging
from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import (
    IncidentCostModelCreate,
    IncidentCostModelPagination,
    IncidentCostModelRead,
    IncidentCostModelUpdate,
)
from .service import create, update, delete

log = logging.getLogger(__name__)

router = APIRouter()


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
):
    """Deletes an incident cost model and its external resources."""
    try:
        delete(incident_cost_model_id=incident_cost_model_id, db_session=db_session)
    except IntegrityError as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[
                {
                    "msg": (
                        f"Incident Cost Model with id {incident_cost_model_id} could not be deleted. "
                    )
                }
            ],
        ) from None
