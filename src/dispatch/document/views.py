from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from dispatch.database import get_db, search_filter_sort_paginate

from .models import DocumentCreate, DocumentPagination, DocumentRead, DocumentUpdate
from .service import create, delete, get, update

router = APIRouter()


@router.get("/", response_model=DocumentPagination)
def get_documents(
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
    Get all documents.
    """
    return search_filter_sort_paginate(
        db_session=db_session,
        model="Document",
        query_str=query_str,
        page=page,
        items_per_page=items_per_page,
        sort_by=sort_by,
        descending=descending,
        fields=fields,
        values=values,
        ops=ops,
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(*, db_session: Session = Depends(get_db), document_id: int):
    """
    Update a document.
    """
    document = get(db_session=db_session, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="The document with this id does not exist.")
    return document


@router.post("/", response_model=DocumentCreate)
def create_document(*, db_session: Session = Depends(get_db), document_in: DocumentCreate):
    """
    Create a new document.
    """
    document = create(db_session=db_session, document_in=document_in)
    return document


@router.put("/{document_id}", response_model=DocumentCreate)
def update_document(
    *, db_session: Session = Depends(get_db), document_id: int, document_in: DocumentUpdate
):
    """
    Update a document.
    """
    document = get(db_session=db_session, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="The document with this id does not exist.")
    document = update(db_session=db_session, document=document, document_in=document_in)
    return document


@router.delete("/{document_id}")
def delete_document(*, db_session: Session = Depends(get_db), document_id: int):
    """
    Delete a document.
    """
    document = get(db_session=db_session, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="The document with this id does not exist.")
    delete(db_session=db_session, document_id=document_id)
