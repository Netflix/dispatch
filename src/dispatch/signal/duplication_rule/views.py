from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.exceptions import ExistsError
from dispatch.models import PrimaryKey
from dispatch.auth.models import DispatchUser
from dispatch.auth import service as auth_service

from .models import (
    DuplicationRuleCreate,
    DuplicationRuleUpdate,
    DuplicationRuleRead,
    DuplicationRulePagination,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=DuplicationRulePagination)
def get_rules(*, common: dict = Depends(common_parameters)):
    """Retrieve rules."""
    return search_filter_sort_paginate(model="DuplicationRule", **common)


@router.post("", response_model=DuplicationRuleRead)
def create_duplication_rule(
    *,
    db_session: Session = Depends(get_db),
    duplication_rule_in: DuplicationRuleCreate,
    current_user: DispatchUser = Depends(auth_service.get_current_user),
):
    """Create a new rule."""
    try:
        return create(
            db_session=db_session,
            duplication_rule_in=duplication_rule_in,
            current_user=current_user,
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A duplication rule with this name already exists."), loc="name"
                )
            ],
            model=DuplicationRuleRead,
        )


@router.put("/{duplication_rule_id}", response_model=DuplicationRuleRead)
def update_duplication_rule(
    *,
    db_session: Session = Depends(get_db),
    duplication_rule_id: PrimaryKey,
    duplication_rule_in: DuplicationRuleUpdate,
):
    """Update a duplication rule."""
    duplication_rule = get(db_session=db_session, duplication_rule_id=duplication_rule_id)
    if not duplication_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A duplication rule with this id does not exist."}],
        )
    try:
        duplication_rule = update(
            db_session=db_session,
            duplication_rule=duplication_rule,
            duplication_rule_in=duplication_rule_in,
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A duplication rule with this name already exists."), loc="name"
                )
            ],
            model=DuplicationRuleUpdate,
        )
    return duplication_rule


@router.delete("/{duplication_rule_id}", response_model=None)
def delete_rule(*, db_session: Session = Depends(get_db), duplication_rule_id: PrimaryKey):
    """Delete a duplication rule."""
    duplication_rule = get(db_session=db_session, duplication_rule_id=duplication_rule_id)
    if not duplication_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A duplication rule with this id does not exist."}],
        )
    delete(db_session=db_session, duplication_rule_id=duplication_rule_id)
