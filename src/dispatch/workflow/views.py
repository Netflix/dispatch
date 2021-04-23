from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from .models import WorkflowPagination, WorkflowRead, WorkflowCreate, WorkflowUpdate
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=WorkflowPagination)
def get_workflows(*, common: dict = Depends(common_parameters)):
    """
    Get all workflows.
    """
    return search_filter_sort_paginate(model="Workflow", **common)


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(*, db_session: Session = Depends(get_db), workflow_id: int):
    """
    Get a workflow.
    """
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="A workflow with this id does not exist.")
    return workflow


@router.post("", response_model=WorkflowCreate)
def create_workflow(*, db_session: Session = Depends(get_db), workflow_in: WorkflowCreate):
    """
    Create a new workflow.
    """
    workflow = create(db_session=db_session, workflow_in=workflow_in)
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowUpdate)
def update_workflow(
    *, db_session: Session = Depends(get_db), workflow_id: int, workflow_in: WorkflowUpdate
):
    """
    Update a workflow.
    """
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="A workflow with this id does not exist.")
    workflow = update(db_session=db_session, workflow=workflow, workflow_in=workflow_in)
    return workflow


@router.delete("/{workflow_id}")
def delete_workflow(*, db_session: Session = Depends(get_db), workflow_id: int):
    """
    Delete a workflow.
    """
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="A workflow with this id does not exist.")
    delete(db_session=db_session, workflow_id=workflow_id)
