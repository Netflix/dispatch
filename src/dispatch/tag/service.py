from typing import Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.tag_type import service as tag_type_service

from .models import Tag, TagCreate, TagUpdate, TagRead


def get(*, db_session, tag_id: int) -> Optional[Tag]:
    """Gets a tag by its id."""
    return db_session.query(Tag).filter(Tag.id == tag_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[Tag]:
    """Gets a tag by its project and name."""
    return (
        db_session.query(Tag)
        .filter(Tag.name == name)
        .filter(Tag.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session, project_id: int, tag_in=TagRead) -> TagRead:
    """Returns the tag specified or raises ValidationError."""
    tag = get_by_name(db_session=db_session, project_id=project_id, name=tag_in.name)

    if not tag:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Tag not found.",
                        tag=tag_in.name,
                    ),
                    loc="tag",
                )
            ],
            model=TagRead,
        )

    return tag


def get_all(*, db_session, project_id: int):
    """Gets all tags by their project."""
    return db_session.query(Tag).filter(Tag.project_id == project_id)


def create(*, db_session, tag_in: TagCreate) -> Tag:
    """Creates a new tag."""
    project = project_service.get_by_name_or_raise(db_session=db_session, project_in=tag_in.project)
    tag_type = tag_type_service.get_or_create(db_session=db_session, tag_type_in=tag_in.tag_type)
    tag = Tag(**tag_in.dict(exclude={"tag_type", "project"}), project=project, tag_type=tag_type)
    tag.tag_type = tag_type
    tag.project = project
    db_session.add(tag)
    db_session.commit()
    return tag


def get_or_create(*, db_session, tag_in: TagCreate) -> Tag:
    """Gets or creates a new tag."""
    # prefer the tag id if available
    if tag_in.id:
        q = db_session.query(Tag).filter(Tag.id == tag_in.id)
    else:
        q = db_session.query(Tag).filter_by(name=tag_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, tag_in=tag_in)


def update(*, db_session, tag: Tag, tag_in: TagUpdate) -> Tag:
    """Updates an existing tag."""
    tag_data = tag.dict()
    update_data = tag_in.dict(skip_defaults=True, exclude={"tag_type"})

    for field in tag_data:
        if field in update_data:
            setattr(tag, field, update_data[field])

    if tag_in.tag_type is not None:
        tag_type = tag_type_service.get_by_name_or_raise(
            db_session=db_session, project_id=tag.project.id, tag_type_in=tag_in.tag_type
        )
        tag.tag_type = tag_type

    db_session.commit()
    return tag


def delete(*, db_session, tag_id: int):
    """Deletes an existing tag."""
    tag = db_session.query(Tag).filter(Tag.id == tag_id).one_or_none()
    db_session.delete(tag)
    db_session.commit()
