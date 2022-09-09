from typing import List, Optional

from sqlalchemy_filters import apply_filters

from dispatch.database.core import Base, get_class_by_tablename, get_table_name_by_class_instance
from dispatch.database.service import apply_filter_specific_joins
from dispatch.project import service as project_service

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


# TODO
def fingerprint(*, db_session, filter_spec: List[dict], class_instance: Base):
    """Creates a fingerprint based on the duplication rule."""
    table_name = get_table_name_by_class_instance(class_instance)
    model_cls = get_class_by_tablename(table_name)
    query = db_session.query(model_cls)

    query = apply_filter_specific_joins(model_cls, filter_spec, query)
    query = apply_filters(query, filter_spec)
    return query.filter(model_cls.id == class_instance.id).one_or_none()


def get_or_create(*, db_session, duplication_rule_in) -> DuplicationRule:
    if duplication_rule_in.id:
        q = db_session.query(DuplicationRule).filter(DuplicationRule.id == duplication_rule_in.id)
    else:
        q = db_session.query(DuplicationRule).filter_by(**duplication_rule_in.dict(exclude={"id"}))

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, duplication_rule_in=duplication_rule_in)


def get_all(*, db_session):
    """Gets all duplication rules."""
    return db_session.query(DuplicationRule)


def create(*, db_session, duplication_rule_in: DuplicationRuleCreate) -> DuplicationRule:
    """Creates a new duplication rule."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=duplication_rule_in.project
    )
    duplication_rule = duplicationRule(
        **duplication_rule_in.dict(exclude={"project"}), project=project
    )
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
