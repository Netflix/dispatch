from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    ProjectPagination,
)
from .service import create, delete, get, get_by_email, update

router = APIRouter()


@router.get("/", response_model=ProjectPagination)
def get_projects(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    fields: List[str] = Query([], alias="fields[]"),
    ops: List[str] = Query([], alias="ops[]"),
    values: List[str] = Query([], alias="values[]"),
):
    """
    Get all project contacts.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Project",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.post("/", response_model=ProjectRead)
def create_project(*, db_session: Session = Depends(get_db), project_in: ProjectCreate):
    """
    Create a new project contact.
    """
    project = get_by_email(db_session=db_session, email=project_in.email)
    if project:
        raise HTTPException(status_code=400, detail="The project with this email already exists.")
    project = create(db_session=db_session, project_in=project_in)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(*, db_session: Session = Depends(get_db), project_id: int):
    """
    Get a project contact.
    """
    project = get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="The project with this id does not exist.")
    return project


@router.put("/{projectg_id}", response_model=ProjectRead)
def update_project(
    *,
    db_session: Session = Depends(get_db),
    project_id: int,
    project_in: ProjectUpdate,
):
    """
    Update a project contact.
    """
    project = get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="The project with this id does not exist.")
    project = update(db_session=db_session, project=project, project_in=project_in)
    return project


@router.delete("/{project_id}", response_model=ProjectRead)
def delete_project(*, db_session: Session = Depends(get_db), project_id: int):
    """
    Delete a project contact.
    """
    project = get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="The project with this id does not exist.")

    delete(db_session=db_session, project_id=project_id)
    return project
