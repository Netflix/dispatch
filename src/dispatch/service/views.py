from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import ServiceCreate, ServicePagination, ServiceRead, ServiceUpdate
from .service import create, delete, get, get_by_external_id, update

router = APIRouter()


@router.get("/", response_model=ServicePagination)
def get_services(
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
    Retrieve all services.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Service",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.post("/", response_model=ServiceRead)
def create_service(
    *,
    db_session: Session = Depends(get_db),
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
    """
    Create a new service.
    """
    service = get_by_external_id(db_session=db_session, external_id=service_in.external_id)
    if service:
        raise HTTPException(
            status_code=400,
            detail=f"The service with this identifier ({service_in.external_id}) already exists.",
        )
    service = create(db_session=db_session, service_in=service_in)
    return service


@router.put("/{service_id}", response_model=ServiceRead)
def update_service(
    *, db_session: Session = Depends(get_db), service_id: int, service_in: ServiceUpdate
):
    """
    Update an existing service.
    """
    service = get(db_session=db_session, service_id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="The service with this id does not exist.")
    service = update(db_session=db_session, service=service, service_in=service_in)
    return service


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(*, db_session: Session = Depends(get_db), service_id: int):
    """
    Get a single service.
    """
    service = get(db_session=db_session, service_id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="The service with this id does not exist.")
    return service


@router.delete("/{service_id}")
def delete_service(*, db_session: Session = Depends(get_db), service_id: int):
    """
    Delete a single service.
    """
    service = get(db_session=db_session, service_id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="The service with this id does not exist.")
    delete(db_session=db_session, service_id=service_id)
