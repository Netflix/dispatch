from typing import Optional

from dispatch.project import service as project_service
from dispatch.auth.models import DispatchUser

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


def match(*, db_session, signal):
    """Find any matching duplication rules and match signals."""
    return
