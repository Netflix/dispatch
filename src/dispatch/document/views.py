from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate

from .models import DocumentCreate, DocumentPagination, DocumentRead, DocumentUpdate
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=DocumentPagination)
def get_documents(*, common: dict = Depends(common_parameters)):
    """
    Get all documents.
    """
    return search_filter_sort_paginate(model="Document", **common)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(*, db_session: Session = Depends(get_db), document_id: int):
    """
    Update a document.
    """
    document = get(db_session=db_session, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="The document with this id does not exist.")
    return document


@router.post("", response_model=DocumentCreate)
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
