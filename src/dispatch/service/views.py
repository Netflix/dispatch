from fastapi import APIRouter, Body, HTTPException, status, Query
from pydantic import ValidationError
from typing import List

from sqlalchemy.exc import IntegrityError

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import ServiceCreate, ServicePagination, ServiceRead, ServiceUpdate
from .service import (
    get,
    create,
    update,
    delete,
    get_by_external_id_and_project_name,
    get_all_by_external_ids,
)


router = APIRouter()


@router.get("", response_model=ServicePagination)
def get_services(common: CommonParameters):
    """Retrieves all services."""
    return search_filter_sort_paginate(model="Service", **common)


@router.get("/externalids", response_model=List[ServiceRead])
def get_services_by_external_ids(
    db_session: DbSession,
    ids: List[str] = Query(..., alias="ids[]"),
):
    """Retrieves all services given list of external ids."""
    return get_all_by_external_ids(db_session=db_session, external_ids=ids)


@router.post("", response_model=ServiceRead)
def create_service(
    db_session: DbSession,
    service_in: ServiceCreate = Body(
        ...,
        example={
            "name": "myService",
            "type": "pagerduty",
            "is_active": True,
            "external_id": "234234",
        },
    ),
):
    """Creates a new service."""
    service = get_by_external_id_and_project_name(
        db_session=db_session,
        external_id=service_in.external_id,
        project_name=service_in.project.name,
    )
    if service:
        raise ValidationError(
            [
                {
                    "msg": "A service with this external id already exists.",
                    "loc": "external_id",
                }
            ],
        )
    service = create(db_session=db_session, service_in=service_in)
    return service


@router.put("/{service_id}", response_model=ServiceRead)
def update_service(db_session: DbSession, service_id: PrimaryKey, service_in: ServiceUpdate):
    """Updates an existing service."""
    service = get(db_session=db_session, service_id=service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A service with this id does not exist."}],
        )

    try:
        service = update(db_session=db_session, service=service, service_in=service_in)
    except IntegrityError:
        raise ValidationError(
            [
                {
                    "msg": "A service with this name already exists.",
                    "loc": "name",
                }
            ],
        ) from None

    return service


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(db_session: DbSession, service_id: PrimaryKey):
    """Gets a service."""
    service = get(db_session=db_session, service_id=service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A service with this id does not exist."}],
        )
    return service


@router.delete("/{service_id}", response_model=None)
def delete_service(db_session: DbSession, service_id: PrimaryKey):
    """Deletes a service."""
    service = get(db_session=db_session, service_id=service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A service with this id does not exist."}],
        )
    try:
        delete(db_session=db_session, service_id=service_id)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[
                {
                    "msg": "Unable to delete service because it is referenced by an incident `Role`. Remove this reference before deletion."
                }
            ],
        ) from None
