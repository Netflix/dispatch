from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from .models import Policy, PolicyCreate, PolicyUpdate
from .dsl import build_parser


def get(*, db_session, policy_id: int) -> Optional[Policy]:
    """Gets a policy by id."""
    return db_session.query(Policy).filter(Policy.id == policy_id).first()


def get_by_name(*, db_session, name: str) -> Optional[Policy]:
    """Gets a policy by name."""
    return db_session.query(Policy).filter(Policy.name == name).first()


def get_by_expression(*, db_session, expression: str) -> Optional[Policy]:
    """Gets a policy by expression."""
    return db_session.query(Policy).filter(Policy.expression == expression).one_or_none()


def get_all(*, db_session):
    """Gets all policies."""
    return db_session.query(Policy)


def create(*, db_session, policy_in: PolicyCreate) -> Policy:
    """Creates a new policy."""
    policy = Policy(**policy_in.dict())
    db_session.add(policy)
    db_session.commit()
    return policy


def create_all(*, db_session, policies_in: List[PolicyCreate]) -> List[Policy]:
    """Creates all policies."""
    policies = [Policy(name=p.name) for p in policies_in]
    db_session.bulk_save_insert(policies)
    db_session.commit()
    db_session.refresh()
    return policies


def update(*, db_session, policy: Policy, policy_in: PolicyUpdate) -> Policy:
    """Updates a policy."""
    policy_data = jsonable_encoder(policy)
    update_data = policy_in.dict(skip_defaults=True)

    for field in policy_data:
        if field in update_data:
            setattr(policy, field, update_data[field])

    db_session.add(policy)
    db_session.commit()
    return policy


def create_or_update(*, db_session, policy_in: PolicyCreate) -> Policy:
    """Creates or updates a policy."""
    update_data = policy_in.dict(skip_defaults=True)

    q = db_session.query(Policy)
    for attr, value in update_data.items():
        q = q.filter(getattr(Policy, attr) == value)

    instance = q.first()

    if instance:
        return update(db_session=db_session, policy=instance, policy_in=policy_in)

    return create(db_session=db_session, policy_in=policy_in)


def parse(policy: str) -> dict:
    """Parse a policy."""
    query = build_parser()
    return query.parseString(policy, parseAll=True)


def delete(*, db_session, policy_id: int):
    """Delets a policy."""
    policy = db_session.query(Policy).filter(Policy.id == policy_id).first()
    db_session.delete(policy)
    db_session.commit()
