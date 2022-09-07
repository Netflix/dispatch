from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.exceptions import NotFoundError
from dispatch.models import PrimaryKey
from dispatch.plugin import service as plugin_service

from .models import WorkflowPagination, WorkflowRead, WorkflowCreate, WorkflowUpdate
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=WorkflowPagination)
def get_workflows(*, common: dict = Depends(common_parameters)):
    """Get all workflows."""
    return search_filter_sort_paginate(model="Workflow", **common)


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(*, db_session: Session = Depends(get_db), workflow_id: PrimaryKey):
    """Get a workflow."""
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workflow with this id does not exist."}],
        )
    return workflow


@router.post("", response_model=WorkflowRead)
def create_workflow(*, db_session: Session = Depends(get_db), workflow_in: WorkflowCreate):
    """Create a new workflow."""
    plugin_instance = plugin_service.get_instance(
        db_session=db_session, plugin_instance_id=workflow_in.plugin_instance.id
    )
    if not plugin_instance:
        raise ValidationError(
            [ErrorWrapper(NotFoundError(msg="No plugin instance found."), loc="plugin_instance")],
            model=WorkflowCreate,
        )

    return create(db_session=db_session, workflow_in=workflow_in)


@router.put("/{workflow_id}", response_model=WorkflowRead)
def update_workflow(
    *, db_session: Session = Depends(get_db), workflow_id: PrimaryKey, workflow_in: WorkflowUpdate
):
    """Update a workflow."""
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workflow with this id does not exist."}],
        )
    return update(db_session=db_session, workflow=workflow, workflow_in=workflow_in)


@router.delete("/{workflow_id}", response_model=None)
def delete_workflow(*, db_session: Session = Depends(get_db), workflow_id: PrimaryKey):
    """Delete a workflow."""
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workflow with this id does not exist."}],
        )
    delete(db_session=db_session, workflow_id=workflow_id)
