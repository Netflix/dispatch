from fastapi import APIRouter, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.exceptions import NotFoundError
from dispatch.models import PrimaryKey
from dispatch.plugin import service as plugin_service

from .models import (
    WorkflowInstanceCreate,
    WorkflowPagination,
    WorkflowRead,
    WorkflowInstanceRead,
    WorkflowCreate,
    WorkflowUpdate,
)
from .service import create, delete, get, update, run, get_instance


router = APIRouter()


@router.get("", response_model=WorkflowPagination)
def get_workflows(common: CommonParameters):
    """Get all workflows."""
    return search_filter_sort_paginate(model="Workflow", **common)


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(db_session: DbSession, workflow_id: PrimaryKey):
    """Get a workflow."""
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workflow with this id does not exist."}],
        )
    return workflow


@router.get("/instances/{workflow_instance_id}", response_model=WorkflowInstanceRead)
def get_workflow_instance(db_session: DbSession, workflow_instance_id: PrimaryKey):
    """Get a workflow instance."""
    workflow_instance = get_instance(db_session=db_session, instance_id=workflow_instance_id)
    if not workflow_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workflow instance with this id does not exist."}],
        )
    return workflow_instance


@router.post("", response_model=WorkflowRead)
def create_workflow(db_session: DbSession, workflow_in: WorkflowCreate):
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
def update_workflow(db_session: DbSession, workflow_id: PrimaryKey, workflow_in: WorkflowUpdate):
    """Update a workflow."""
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workflow with this id does not exist."}],
        )
    return update(db_session=db_session, workflow=workflow, workflow_in=workflow_in)


@router.delete("/{workflow_id}", response_model=None)
def delete_workflow(db_session: DbSession, workflow_id: PrimaryKey):
    """Delete a workflow."""
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workflow with this id does not exist."}],
        )
    delete(db_session=db_session, workflow_id=workflow_id)


@router.post("/{workflow_id}/run", response_model=WorkflowInstanceRead)
def run_workflow(
    db_session: DbSession,
    workflow_id: PrimaryKey,
    workflow_instance_in: WorkflowInstanceCreate,
):
    """Runs a workflow with a given set of parameters."""
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A workflow with this id does not exist."}],
        )
    return run(db_session=db_session, workflow=workflow, workflow_instance_in=workflow_instance_in)
