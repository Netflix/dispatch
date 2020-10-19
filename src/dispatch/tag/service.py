from typing import Optional
from fastapi.encoders import jsonable_encoder

from dispatch.tag_type import service as tag_type_service

from .models import Tag, TagCreate, TagUpdate


def get(*, db_session, tag_id: int) -> Optional[Tag]:
    return db_session.query(Tag).filter(Tag.id == tag_id).one_or_none()


def get_by_name(*, db_session, name: str) -> Optional[Tag]:
    return db_session.query(Tag).filter(Tag.name == name).one_or_none()


def get_all(*, db_session):
    return db_session.query(Tag)


def create(*, db_session, tag_in: TagCreate) -> Tag:
    tag_type = tag_type_service.get_by_name(
        db_session=db_session, tag_type_name=tag_in.tag_type.name
    )
    tag = Tag(**tag_in.dict(exclude={"tag_type"}), tag_type=tag_type)
    db_session.add(tag)
    db_session.commit()
    return tag


def get_or_create(*, db_session, tag_in: TagCreate) -> Tag:
    q = db_session.query(Tag).filter_by(name=tag_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, tag_in=tag_in)


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
