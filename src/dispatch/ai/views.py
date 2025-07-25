import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import ValidationError

from sqlalchemy.exc import IntegrityError

from dispatch.auth.permissions import (
    SensitiveProjectActionPermission,
    PermissionsDependency,
)
from dispatch.database.core import DbSession
from dispatch.auth.service import CurrentUser
from dispatch.database.service import search_filter_sort_paginate, CommonParameters
from dispatch.models import PrimaryKey

from .models import (
    PromptRead,
    PromptUpdate,
    PromptPagination,
    PromptCreate,
)
from .service import get, create, update, delete
from .strings import DEFAULT_PROMPTS, DEFAULT_SYSTEM_MESSAGES

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=PromptPagination)
def get_prompts(commons: CommonParameters):
    """Get all AI prompts, or only those matching a given search term."""
    return search_filter_sort_paginate(model="Prompt", **commons)


@router.get("/defaults")
def get_default_prompts():
    """Get default prompts and system messages for different GenAI types."""
    return {
        "prompts": DEFAULT_PROMPTS,
        "system_messages": DEFAULT_SYSTEM_MESSAGES,
    }


@router.get("/{prompt_id}", response_model=PromptRead)
def get_prompt(db_session: DbSession, prompt_id: PrimaryKey):
    """Get an AI prompt by its id."""
    prompt = get(db_session=db_session, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An AI prompt with this id does not exist."}],
        )
    return prompt


@router.post(
    "",
    response_model=PromptRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_prompt(
    db_session: DbSession,
    prompt_in: PromptCreate,
    current_user: CurrentUser,
):
    """Create a new AI prompt."""
    try:
        return create(db_session=db_session, prompt_in=prompt_in)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "An AI prompt with this configuration already exists.", "loc": "genai_type"}],
        ) from None


@router.put(
    "/{prompt_id}",
    response_model=PromptRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_prompt(
    db_session: DbSession,
    prompt_id: PrimaryKey,
    prompt_in: PromptUpdate,
):
    """Update an AI prompt."""
    prompt = get(db_session=db_session, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An AI prompt with this id does not exist."}],
        )
    try:
        prompt = update(
            db_session=db_session,
            prompt=prompt,
            prompt_in=prompt_in,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "An AI prompt with this configuration already exists.", "loc": "genai_type"}],
        )
    return prompt


@router.delete(
    "/{prompt_id}",
    response_model=None,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_prompt(db_session: DbSession, prompt_id: PrimaryKey):
    """Delete an AI prompt, returning only an HTTP 200 OK if successful."""
    prompt = get(db_session=db_session, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "An AI prompt with this id does not exist."}],
        )
    delete(db_session=db_session, prompt_id=prompt_id)
