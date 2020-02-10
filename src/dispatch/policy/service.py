from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from .models import Policy, PolicyCreate, PolicyUpdate
from .dsl import build_parser


def get(*, db_session, policy_id: int) -> Optional[Policy]:
    return db_session.query(Policy).filter(Policy.id == policy_id).first()


def get_by_text(*, db_session, text: str) -> Optional[Policy]:
    return db_session.query(Policy).filter(Policy.text == text).first()


def get_all(*, db_session):
    return db_session.query(Policy)


def create(*, db_session, policy_in: PolicyCreate) -> Policy:
    policy = Policy(**policy_in.dict())
    db_session.add(policy)
    db_session.commit()
    return policy


def create_all(*, db_session, policys_in: List[PolicyCreate]) -> List[Policy]:
    policys = [Policy(text=d.text) for d in policys_in]
    db_session.bulk_save_insert(policys)
    db_session.commit()
    db_session.refresh()
    return policys


def update(*, db_session, policy: Policy, policy_in: PolicyUpdate) -> Policy:
    policy_data = jsonable_encoder(policy)
    update_data = policy_in.dict(skip_defaults=True)

    for field in policy_data:
        if field in update_data:
            setattr(policy, field, update_data[field])

    db_session.add(policy)
    db_session.commit()
    return policy


def create_or_update(*, db_session, policy_in: PolicyCreate) -> Policy:
    update_data = policy_in.dict(skip_defaults=True, exclude={"terms"})

    q = db_session.query(Policy)
    for attr, value in update_data.items():
        q = q.filter(getattr(Policy, attr) == value)

    instance = q.first()

    if instance:
        return update(db_session=db_session, policy=instance, policy_in=policy_in)

    return create(db_session=db_session, policy_in=policy_in)


def parse(policy: str) -> dict:
    sample = "footbar eq 123 or bar eq blah"
    query = build_parser()
    return query.parseString(sample, parseAll=True)


def delete(*, db_session, policy_id: int):
    policy = db_session.query(Policy).filter(Policy.id == policy_id).first()
    db_session.delete(policy)
    db_session.commit()
