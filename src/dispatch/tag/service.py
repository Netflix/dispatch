from typing import Optional
from fastapi.encoders import jsonable_encoder

from dispatch.project import service as project_service
from dispatch.tag_type import service as tag_type_service

from .models import Tag, TagCreate, TagUpdate


def get(*, db_session, tag_id: int) -> Optional[Tag]:
    return db_session.query(Tag).filter(Tag.id == tag_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[Tag]:
    return (
        db_session.query(Tag)
        .filter(Tag.name == name)
        .filter(Tag.project_id == project_id)
        .one_or_none()
    )


def get_all(*, db_session, project_id: int):
    return db_session.query(Tag).filter(Tag.project_id == project_id)


def create(*, db_session, tag_in: TagCreate) -> Tag:
    project = project_service.get_by_name(db_session=db_session, name=tag_in.project.name)
    tag_type = tag_type_service.get_by_name(
        db_session=db_session, project_id=project.id, name=tag_in.tag_type.name
    )
    tag = Tag(**tag_in.dict(exclude={"tag_type", "project"}), project=project, tag_type=tag_type)
    tag.tag_type = tag_type
    tag.project = project
    db_session.add(tag)
    db_session.commit()
    return tag


def get_or_create(*, db_session, tag_in: TagCreate) -> Tag:
    # prefer the  ID if available
    if tag_in.id:
        q = db_session.query(Tag).filter(Tag.id == tag_in.id)
    else:
        q = db_session.query(Tag).filter_by(name=tag_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, tag_in=tag_in)


def update(*, db_session, tag: Tag, tag_in: TagUpdate) -> Tag:
    tag_data = jsonable_encoder(tag)
    update_data = tag_in.dict(skip_defaults=True, exclude={"tag_type"})

    tag_type = tag_type_service.get_by_name(
        db_session=db_session, project_id=tag.project.id, name=tag_in.tag_type.name
    )

    for field in tag_data:
        if field in update_data:
            setattr(tag, field, update_data[field])

    tag.tag_type = tag_type

    db_session.add(tag)
    db_session.commit()
    return tag


def delete(*, db_session, tag_id: int):
    tag = db_session.query(Tag).filter(Tag.id == tag_id).one_or_none()
    db_session.delete(tag)
    db_session.commit()
