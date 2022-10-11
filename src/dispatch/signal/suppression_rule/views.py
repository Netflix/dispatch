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
    SuppressionRuleCreate,
    SuppressionRuleUpdate,
    SuppressionRuleRead,
    SuppressionRulePagination,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=SuppressionRulePagination)
def get_rules(*, common: dict = Depends(common_parameters)):
    """Retrieve filters."""
    return search_filter_sort_paginate(model="SuppressionRule", **common)


@router.post("", response_model=SuppressionRuleRead)
def create_suppression_rule(
    *,
    db_session: Session = Depends(get_db),
    suppression_rule_in: SuppressionRuleCreate,
    current_user: DispatchUser = Depends(auth_service.get_current_user),
):
    """Create a new filter."""
    try:
        return create(
            db_session=db_session,
            suppression_rule_in=suppression_rule_in,
            current_user=current_user,
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A suppression rule with this name already exists."), loc="name"
                )
            ],
            model=SuppressionRuleRead,
        )


@router.put("/{suppression_rule_id}", response_model=SuppressionRuleRead)
def update_suppression_rule(
    *,
    db_session: Session = Depends(get_db),
    suppression_rule_id: PrimaryKey,
    suppression_rule_in: SuppressionRuleUpdate,
):
    """Update a suppression rule."""
    suppression_rule = get(db_session=db_session, suppression_rule_id=suppression_rule_id)
    if not suppression_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A suppression rule with this id does not exist."}],
        )
    try:
        suppression_rule = update(
            db_session=db_session,
            suppression_rule=suppression_rule,
            suppression_rule_in=suppression_rule_in,
        )
    except IntegrityError:
        raise ValidationError(
            [
                ErrorWrapper(
                    ExistsError(msg="A suppression rule with this name already exists."), loc="name"
                )
            ],
            model=SuppressionRuleUpdate,
        )
    return suppression_rule


@router.delete("/{suppression_rule_id}", response_model=None)
def delete_rule(*, db_session: Session = Depends(get_db), suppression_rule_id: PrimaryKey):
    """Delete a suppression rule."""
    suppression_rule = get(db_session=db_session, suppression_rule_id=suppression_rule_id)
    if not suppression_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A suppression rule with this id does not exist."}],
        )
    delete(db_session=db_session, suppression_rule_id=suppression_rule_id)
