import hashlib
from typing import Optional
from datetime import datetime, timedelta

from dispatch.enums import RuleMode

from dispatch.project import service as project_service
from dispatch.auth.models import DispatchUser

from dispatch.signal.models import Signal

from .models import DuplicationRule, DuplicationRuleCreate, DuplicationRuleUpdate


def get(*, db_session, duplication_rule_id: int) -> Optional[DuplicationRule]:
    """Gets a duplication rule by id."""
    return (
        db_session.query(DuplicationRule).filter(DuplicationRule.id == duplication_rule_id).first()
    )


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[DuplicationRule]:
    """Gets a duplication rule by name."""
    return (
        db_session.query(DuplicationRule)
        .filter(DuplicationRule.name == name)
        .filter(DuplicationRule.project_id == project_id)
        .first()
    )


def get_active(*, db_session, project_id: int, signal_name: str) -> Optional[DuplicationRule]:
    """Gets active duplicate rules for a given signal."""
    return (
        db_session.query(DuplicationRule)
        .filter(DuplicationRule.signal_name == signal_name)
        .filter(DuplicationRule.project_id == project_id)
        .filter(DuplicationRule.mode == RuleMode.active)
        .one()
    )


def get_all(*, db_session):
    """Gets all duplication rules."""
    return db_session.query(DuplicationRule)


def create(
    *, db_session, duplication_rule_in: DuplicationRuleCreate, current_user: DispatchUser
) -> DuplicationRule:
    """Creates a new duplication rule."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=duplication_rule_in.project
    )
    duplication_rule = DuplicationRule(
        **duplication_rule_in.dict(exclude={"project"}), project=project
    )
    duplication_rule.creator = current_user
    db_session.add(duplication_rule)
    db_session.commit()
    return duplication_rule


def update(
    *, db_session, duplication_rule: DuplicationRule, duplication_rule_in: DuplicationRuleUpdate
) -> DuplicationRule:
    """Updates a duplication rule."""
    duplication_rule_data = duplication_rule.dict()
    update_data = duplication_rule_in.dict(skip_defaults=True)

    for field in duplication_rule_data:
        if field in update_data:
            setattr(duplication_rule, field, update_data[field])

    db_session.commit()
    return duplication_rule


def delete(*, db_session, duplication_rule_id: int):
    """Deletes a duplication rule."""
    duplication_rule = (
        db_session.query(DuplicationRule).filter(DuplicationRule.id == duplication_rule_id).first()
    )
    db_session.delete(duplication_rule)
    db_session.commit()


def create_fingerprint(tag_types, tags):
    """Given a list of tag_types and tags creates a hash of their values."""
    tag_values = []
    tag_type_names = [t.name for t in tag_types]
    for tag in tags:
        if tag.tag_type.name in tag_type_names:
            tag_values = tag.tag_type.name

    return hashlib.sha1("-".join(sorted(tag_values)))


def deduplicate(*, db_session, signal):
    """Find any matching duplication rules and match signals."""
    duplicate = False
    rule = get_active(db_session=db_session, signal_name=signal.name)

    if not rule:
        return duplicate

    window = datetime.now() - timedelta(seconds=rule.window)

    fingerprint = create_fingerprint(rule.tag_types, signal.tags)
    signal.fingerprint = fingerprint

    signals = (
        db_session.query(Signal)
        .filter(Signal.created_at >= window)
        .filter(Signal.detection == signal.detection)
        .filter(Signal.detection_variant == signal.detection_variant)
        .filter(Signal.fingerprint == signal.fingerprint)
        .all()
    )

    if signals:
        duplicate = True
        signal.case_id = signals[0].case_id
        signal.duplication_rule_id = rule.id

    db_session.commit()
    return duplicate
