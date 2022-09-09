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
    SupressionRuleCreate,
    SupressionRuleUpdate,
    SupressionRuleRead,
    SupressionRulePagination,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=SupressionRulePagination)
def get_ruless(*, common: dict = Depends(common_parameters)):
    """Retrieve filters."""
    return search_filter_sort_paginate(model="SupressionRule", **common)


@router.post("", response_model=SupressionRuleRead)
def create_supression_rule(
    *,
    db_session: Session = Depends(get_db),
    supression_rule_in: SupressionRuleCreate,
    current_user: DispatchUser = Depends(auth_service.get_current_user),
):
    """Create a new filter."""
    try:
        return create(
            db_session=db_session, supression_rule_in=supression_rule_in, current_user=current_user
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A supression rule with this name already exists."), loc="name"
                )
            ],
            model=SupressionRuleRead,
        )


@router.put("/{supression_rule_id}", response_model=SupressionRuleRead)
def update_supression_rule(
    *,
    db_session: Session = Depends(get_db),
    supression_rule_id: PrimaryKey,
    supression_rule_in: SupressionRuleUpdate,
):
    """Update a supression rule."""
    supression_rule = get(db_session=db_session, supression_rule_id=supression_rule_id)
    if not supression_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A supression rule with this id does not exist."}],
        )
    try:
        supression_rule = update(
            db_session=db_session,
            supression_rule=supression_rule,
            supression_rule_in=supression_rule_in,
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A supression rule with this name already exists."), loc="name"
                )
            ],
            model=SupressionRuleUpdate,
        )
    return supression_rule


@router.delete("/{supression_rule_id}", response_model=None)
def delete_rule(*, db_session: Session = Depends(get_db), supression_rule_id: PrimaryKey):
    """Delete a supression rule."""
    supression_rule = get(db_session=db_session, supression_rule_id=supression_rule_id)
    if not supression_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A supression rule with this id does not exist."}],
        )
    delete(db_session=db_session, supression_rule_id=supression_rule_id)
