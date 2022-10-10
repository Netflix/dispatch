from datetime import datetime, timedelta
from typing import Optional

from dispatch.enums import RuleMode
from dispatch.auth.models import DispatchUser

from dispatch.project import service as project_service
from dispatch.signal.models import Signal

from .models import SuppressionRule, SuppressionRuleCreate, SuppressionRuleUpdate


def get(*, db_session, suppression_rule_id: int) -> Optional[SuppressionRule]:
    """Gets a suppression rule by id."""
    return (
        db_session.query(SuppressionRule).filter(SuppressionRule.id == suppression_rule_id).first()
    )


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[SuppressionRule]:
    """Gets a suppression rule by name."""
    return (
        db_session.query(SuppressionRule)
        .filter(SuppressionRule.name == name)
        .filter(SuppressionRule.project_id == project_id)
        .first()
    )


def get_active(*, db_session, project_id: int, signal_name: str) -> Optional[SuppressionRule]:
    """Gets active suppression rules for a given signal."""
    return (
        db_session.query(SuppressionRule)
        .filter(SuppressionRule.signal_name == signal_name)
        .filter(SuppressionRule.project_id == project_id)
        .filter(SuppressionRule.mode == RuleMode.active)
        .one()
    )


def get_all(*, db_session):
    """Gets all suppression rules."""
    return db_session.query(SuppressionRule)


def get_all_active(*, db_session):
    """Gets all active suppression rules."""
    current_time = datetime.utcnow()

    return (
        db_session.query(SuppressionRule)
        .filter(SuppressionRule.mode == RuleMode.active)
        .filter(SuppressionRule.expiration > current_time)
        .all()
    )


def create(
    *, db_session, suppression_rule_in: SuppressionRuleCreate, current_user: DispatchUser
) -> SuppressionRule:
    """Creates a new suppression rule."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=suppression_rule_in.project
    )
    suppression_rule = SuppressionRule(
        **suppression_rule_in.dict(exclude={"project"}), project=project
    )
    suppression_rule.creator = current_user
    db_session.add(suppression_rule)
    db_session.commit()
    return suppression_rule


def update(
    *, db_session, suppression_rule: SuppressionRule, suppression_rule_in: SuppressionRuleUpdate
) -> SuppressionRule:
    """Updates a suppression rule."""
    suppression_rule_data = suppression_rule.dict()
    update_data = suppression_rule_in.dict(skip_defaults=True)

    for field in suppression_rule_data:
        if field in update_data:
            setattr(suppression_rule, field, update_data[field])

    db_session.commit()
    return suppression_rule


def delete(*, db_session, suppression_rule_id: int):
    """Deletes a suppression rule."""
    suppression_rule = (
        db_session.query(SuppressionRule).filter(SuppressionRule.id == suppression_rule_id).first()
    )
    db_session.delete(suppression_rule)
    db_session.commit()


def supress(*, db_session, signal):
    """Find any matching suppression rules and match signals."""
    supressed = False
    rule = get_active(db_session=db_session, signal_name=signal.name)

    if not rule:
        return supressed

    if rule.expiration:
        if rule.expiration <= datetime.now():
            return supressed

    if fingerprint == suppression_hash:
        supressed = True
        signal.suppression_rule_id = rule.id

    db_session.commit()
    return supressed
