from typing import Optional
from fastapi.encoders import jsonable_encoder

from .models import Tag, TagCreate, TagUpdate


def get(*, db_session, tag_id: int) -> Optional[Tag]:
    return db_session.query(Tag).filter(Tag.id == tag_id).one_or_none()


def get_by_name(*, db_session, name: str) -> Optional[Tag]:
    return db_session.query(Tag).filter(Tag.name == name).one_or_none()


def get_all(*, db_session):
    return db_session.query(Tag)


def create(*, db_session, tag_in: TagCreate) -> Tag:
    tag = Tag(**tag_in.dict())
    db_session.add(tag)
    db_session.commit()
    return tag


def update(*, db_session, tag: Tag, tag_in: TagUpdate) -> Tag:
    tag_data = jsonable_encoder(tag)
    update_data = tag_in.dict(skip_defaults=True)

    for field in tag_data:
        if field in update_data:
            setattr(tag, field, update_data[field])

    db_session.add(tag)
    db_session.commit()
    return tag


def delete(*, db_session, tag_id: int):
    tag = db_session.query(Tag).filter(Tag.id == tag_id).one_or_none()
    db_session.delete(tag)
    db_session.commit()
