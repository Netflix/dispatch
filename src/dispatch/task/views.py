from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.common.utils.views import create_pydantic_include
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from .models import TaskCreate, TaskUpdate, TaskRead, TaskPagination
from .service import get, update, create, delete

router = APIRouter()


@router.get("", summary="Retrieve a list of all tasks.")
def get_tasks(
    *, include: List[str] = Query([], alias="include[]"), commons: dict = Depends(common_parameters)
):
    """
    Retrieve all tasks.
    """
    pagination = search_filter_sort_paginate(model="Task", **commons)

    if include:
        # only allow two levels for now
        include_sets = create_pydantic_include(include)

        include_fields = {
            "items": {"__all__": include_sets},
            "itemsPerPage": ...,
            "page": ...,
            "total": ...,
        }

        return TaskPagination(**pagination).dict(include=include_fields)
    return TaskPagination(**pagination).dict()


@router.post("", response_model=TaskRead, tags=["tasks"])
def create_task(
    *,
    db_session: Session = Depends(get_db),
    task_in: TaskCreate,
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Creates a new task.
    """
    task_in.creator = {"individual": {"email": current_user.email}}
    task = create(db_session=db_session, task_in=task_in)
    return task


@router.put("/{task_id}", response_model=TaskRead, tags=["tasks"])
def update_task(*, db_session: Session = Depends(get_db), task_id: int, task_in: TaskUpdate):
    """
    Updates an existing task.
    """
    task = get(db_session=db_session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="A task with this id does not exist.")
    task = update(db_session=db_session, task=task, task_in=task_in)
    return task


@router.delete("/{task_id}", response_model=TaskRead, tags=["tasks"])
def delete_task(*, db_session: Session = Depends(get_db), task_id: int):
    """
    Deletes an existing task.
    """
    task = get(db_session=db_session, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="A task with this id does not exist.")
    delete(db_session=db_session, task_id=task_id)
    return task
