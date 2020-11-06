from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session
from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user

from dispatch.database import get_db, search_filter_sort_paginate

from .models import TaskCreate, TaskUpdate, TaskRead, TaskPagination
from .service import get, update, create, delete

router = APIRouter()


@router.get("/", response_model=TaskPagination, tags=["tasks"])
def get_tasks(
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
    Retrieve all tasks.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Task",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
        join_attrs=[
            ("incident", "incident"),
            ("incident_type", "incident"),
            ("incident_priority", "incident"),
            ("tags", "tag"),
            ("creator", "creator"),
            ("owner", "owner"),
        ],
    )


@router.post("/", response_model=TaskRead, tags=["tasks"])
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
