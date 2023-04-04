from fastapi import APIRouter, HTTPException, status

from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.models import PrimaryKey

from .models import DocumentCreate, DocumentPagination, DocumentRead, DocumentUpdate
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=DocumentPagination)
def get_documents(common: CommonParameters):
    """Get all documents."""
    return search_filter_sort_paginate(model="Document", **common)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(db_session: DbSession, document_id: PrimaryKey):
    """Update a document."""
    document = get(db_session=db_session, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A document with this id does not exist."}],
        )
    return document


@router.post("", response_model=DocumentRead)
def create_document(db_session: DbSession, document_in: DocumentCreate):
    """Create a new document."""
    return create(db_session=db_session, document_in=document_in)


@router.put("/{document_id}", response_model=DocumentRead)
def update_document(db_session: DbSession, document_id: PrimaryKey, document_in: DocumentUpdate):
    """Update a document."""
    document = get(db_session=db_session, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A document with this id does not exist."}],
        )
    document = update(db_session=db_session, document=document, document_in=document_in)
    return document


@router.delete("/{document_id}", response_model=None)
def delete_document(db_session: DbSession, document_id: PrimaryKey):
    """Delete a document."""
    document = get(db_session=db_session, document_id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A document with this id does not exist."}],
        )
    delete(db_session=db_session, document_id=document_id)
