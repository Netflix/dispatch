from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import WorkflowPagination, WorkflowRead, WorkflowCreate, WorkflowUpdate
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=WorkflowPagination)
def get_workflows(
    db_session: Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    sort_by: List[str] = Query(None, alias="sortBy[]"),
    descending: List[bool] = Query(None, alias="descending[]"),
    fields: List[str] = Query(None, alias="field[]"),
    ops: List[str] = Query(None, alias="op[]"),
    values: List[str] = Query(None, alias="value[]"),
):
    """
    Get all documents.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Workflow",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(*, db_session: Session = Depends(get_db), document_id: int):
    """
    Get a workflow.
    """
    document = get(db_session=db_session, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="The document with this id does not exist.")
    return document


@router.post("/", response_model=WorkflowCreate)
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
        raise HTTPException(status_code=404, detail="The workflow with this id does not exist.")
    workflow = update(db_session=db_session, workflow=workflow, workflow_in=workflow_in)
    return workflow


@router.delete("/{workflow_id}")
def delete_workflow(*, db_session: Session = Depends(get_db), workflow_id: int):
    """
    Delete a workflow.
    """
    workflow = get(db_session=db_session, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="The workflow with this id does not exist.")
    delete(db_session=db_session, workflow_id=workflow_id)
