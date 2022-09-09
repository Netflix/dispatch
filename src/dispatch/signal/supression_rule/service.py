from typing import List, Optional

from sqlalchemy_filters import apply_filters
from dispatch.auth.models import DispatchUser

from dispatch.database.core import Base, get_class_by_tablename, get_table_name_by_class_instance
from dispatch.database.service import apply_filter_specific_joins
from dispatch.project import service as project_service

from .models import SupressionRule, SupressionRuleCreate, SupressionRuleUpdate


def get(*, db_session, supression_rule_id: int) -> Optional[SupressionRule]:
    """Gets a supression rule by id."""
    return db_session.query(SupressionRule).filter(SupressionRule.id == supression_rule_id).first()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[SupressionRule]:
    """Gets a supression rule by name."""
    return (
        db_session.query(SupressionRule)
        .filter(SupressionRule.name == name)
        .filter(SupressionRule.project_id == project_id)
        .first()
    )


def match(*, db_session, filter_spec: List[dict], class_instance: Base):
    """Matches a class instance with a given supression rule."""
    table_name = get_table_name_by_class_instance(class_instance)
    model_cls = get_class_by_tablename(table_name)
    query = db_session.query(model_cls)

    query = apply_filter_specific_joins(model_cls, filter_spec, query)
    query = apply_filters(query, filter_spec)
    return query.filter(model_cls.id == class_instance.id).one_or_none()


def get_all(*, db_session):
    """Gets all supression rules."""
    return db_session.query(SupressionRule)


def create(
    *, db_session, supression_rule_in: SupressionRuleCreate, current_user: DispatchUser
) -> SupressionRule:
    """Creates a new supression rule."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=supression_rule_in.project
    )
    supression_rule = SupressionRule(
        **supression_rule_in.dict(exclude={"project"}), project=project
    )
    supression_rule.creator = current_user
    db_session.add(supression_rule)
    db_session.commit()
    return supression_rule


def update(
    *, db_session, supression_rule: SupressionRule, supression_rule_in: SupressionRuleUpdate
) -> SupressionRule:
    """Updates a supression rule."""
    supression_rule_data = supression_rule.dict()
    update_data = supression_rule_in.dict(skip_defaults=True)

    for field in supression_rule_data:
        if field in update_data:
            setattr(supression_rule, field, update_data[field])

    db_session.commit()
    return supression_rule


def delete(*, db_session, supression_rule_id: int):
    """Deletes a supression rule."""
    supression_rule = (
        db_session.query(SupressionRule).filter(SupressionRule.id == supression_rule_id).first()
    )
    db_session.delete(supression_rule)
    db_session.commit()
