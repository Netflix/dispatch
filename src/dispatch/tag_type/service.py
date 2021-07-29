from typing import Optional

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from dispatch.exceptions import NotFoundError

from dispatch.project import service as project_service

from .models import TagType, TagTypeCreate, TagTypeRead, TagTypeUpdate


def get(*, db_session, tag_type_id: int) -> Optional[TagType]:
    """Gets a tag type by its id."""
    return db_session.query(TagType).filter(TagType.id == tag_type_id).one_or_none()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[TagType]:
    """Gets a tag type by its name."""
    return (
        db_session.query(TagType)
        .filter(TagType.name == name)
        .filter(TagType.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(*, db_session, project_id: int, tag_type_in=TagTypeRead) -> TagType:
    """Returns the tag_type specified or raises ValidationError."""
    tag_type = get_by_name(db_session=db_session, project_id=project_id, name=tag_type_in.name)

    if not tag_type:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="TagType not found.", tag_type=tag_type_in.name),
                    loc="tag_type",
                )
            ],
            model=TagTypeRead,
        )

    return tag_type


def get_all(*, db_session):
    """Gets all tag types."""
    return db_session.query(TagType)


def create(*, db_session, tag_type_in: TagTypeCreate) -> TagType:
    """Creates a new tag type."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=tag_type_in.project
    )
    tag_type = TagType(**tag_type_in.dict(exclude={"project"}), project=project)
    db_session.add(tag_type)
    db_session.commit()
    return tag_type


def get_or_create(*, db_session, tag_type_in: TagTypeCreate) -> TagType:
    """Gets or creates a new tag type."""
    q = (
        db_session.query(TagType)
        .filter(TagType.name == tag_type_in.name)
        .filter(TagType.project_id == tag_type_in.project.id)
    )

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, tag_type_in=tag_type_in)


def update(*, db_session, tag_type: TagType, tag_type_in: TagTypeUpdate) -> TagType:
    """Updates a tag type."""
    tag_type_data = tag_type.dict()
    update_data = tag_type_in.dict(skip_defaults=True)

    for field in tag_type_data:
        if field in update_data:
            setattr(tag_type, field, update_data[field])

    db_session.commit()
    return tag_type


def delete(*, db_session, tag_type_id: int):
    """Deletes a tag type."""
    tag = db_session.query(TagType).filter(TagType.id == tag_type_id).one_or_none()
    db_session.delete(tag)
    db_session.commit()
