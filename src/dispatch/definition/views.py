from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dispatch.database.base import get_db
from dispatch.database.service import paginate
from dispatch.search.service import search

from .models import (
    Definition,
    DefinitionCreate,
    DefinitionPagination,
    DefinitionRead,
    DefinitionUpdate,
)
from .service import create, delete, get, get_all, get_by_text, update

router = APIRouter()


@router.get("/", response_model=DefinitionPagination)
def get_definitions(
    db_session: Session = Depends(get_db), page: int = 1, itemsPerPage: int = 5, q: str = None
):
    """
    Get all definitions.
    """
    if q:
        query = search(db_session=db_session, query_str=q, model=Definition)
    else:
        query = get_all(db_session=db_session)

    items, total = paginate(query=query, page=page, items_per_page=itemsPerPage)
    return {"items": items, "total": total}


@router.get("/{definition_id}", response_model=DefinitionRead)
def get_definition(*, db_session: Session = Depends(get_db), definition_id: int):
    """
    Update a definition.
    """
    definition = get(db_session=db_session, definition_id=definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="The definition with this id does not exist.")
    return definition


@router.post("/", response_model=DefinitionRead)
def create_definition(*, db_session: Session = Depends(get_db), definition_in: DefinitionCreate):
    """
    Create a new definition.
    """
    definition = get_by_text(db_session=db_session, text=definition_in.text)
    if definition:
        raise HTTPException(
            status_code=400,
            detail=f"The description with this text ({definition_in.text}) already exists.",
        )
    definition = create(db_session=db_session, definition_in=definition_in)
    return definition


@router.put("/{definition_id}", response_model=DefinitionRead)
def update_definition(
    *, db_session: Session = Depends(get_db), definition_id: int, definition_in: DefinitionUpdate
):
    """
    Update a definition.
    """
    definition = get(db_session=db_session, definition_id=definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="The definition with this id does not exist.")
    definition = update(db_session=db_session, definition=definition, definition_in=definition_in)
    return definition


@router.delete("/{definition_id}")
def delete_definition(*, db_session: Session = Depends(get_db), definition_id: int):
    """
    Delete a definition.
    """
    definition = get(db_session=db_session, definition_id=definition_id)
    if not definition:
        raise HTTPException(status_code=404, detail="The definition with this id does not exist.")
    delete(db_session=db_session, definition_id=definition_id)
