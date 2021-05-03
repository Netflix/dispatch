from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.auth.permissions import (
    ProjectCreatePermission,
    PermissionsDependency,
    ProjectUpdatePermission,
)

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from .models import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    ProjectPagination,
)
from .service import create, delete, get, get_by_name, update

router = APIRouter()


@router.get("", response_model=ProjectPagination)
def get_projects(common: dict = Depends(common_parameters)):
    """
    Get all projects.
    """
    return search_filter_sort_paginate(model="Project", **common)


@router.post(
    "",
    response_model=ProjectRead,
    summary="Create a new project.",
    dependencies=[Depends(PermissionsDependency([ProjectCreatePermission]))],
)
def create_project(*, db_session: Session = Depends(get_db), project_in: ProjectCreate):
    """
    Create a new project.
    """
    project = get_by_name(db_session=db_session, name=project_in.name)
    if project:
        raise HTTPException(status_code=400, detail="A project with this name already exists.")
    project = create(db_session=db_session, project_in=project_in)
    return project


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Get a project.",
)
def get_project(*, db_session: Session = Depends(get_db), project_id: int):
    """
    Get a project.
    """
    project = get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="A project with this id does not exist.")
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    dependencies=[Depends(PermissionsDependency([ProjectUpdatePermission]))],
)
def update_project(
    *,
    db_session: Session = Depends(get_db),
    project_id: int,
    project_in: ProjectUpdate,
):
    """
    Update a project.
    """
    project = get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="A project with this id does not exist.")
    project = update(db_session=db_session, project=project, project_in=project_in)
    return project


@router.delete(
    "/{project_id}",
    response_model=ProjectRead,
    dependencies=[Depends(PermissionsDependency([ProjectUpdatePermission]))],
)
def delete_project(*, db_session: Session = Depends(get_db), project_id: int):
    """
    Delete a project.
    """
    project = get(db_session=db_session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="A project with this id does not exist.")

    delete(db_session=db_session, project_id=project_id)
    return project
