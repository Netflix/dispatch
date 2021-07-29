from typing import Optional

from .models import Group, GroupCreate, GroupUpdate


def get(*, db_session, group_id: int) -> Optional[Group]:
    """Returns a group given a group id."""
    return db_session.query(Group).filter(Group.id == group_id).one_or_none()


def get_by_incident_id_and_resource_type(
    *, db_session, incident_id: str, resource_type: str
) -> Optional[Group]:
    """Returns a group given an incident id and group resource type."""
    return (
        db_session.query(Group)
        .filter(Group.incident_id == incident_id)
        .filter(Group.resource_type == resource_type)
        .one_or_none()
    )


def get_all(*, db_session):
    """Returns all groups."""
    return db_session.query(Group)


def create(*, db_session, group_in: GroupCreate) -> Group:
    """Creates a new group."""
    group = Group(**group_in.dict())
    db_session.add(group)
    db_session.commit()
    return group


def update(*, db_session, group: Group, group_in: GroupUpdate) -> Group:
    """Updates a group."""
    group_data = group.dict()
    update_data = group_in.dict(skip_defaults=True)

    for field in group_data:
        if field in update_data:
            setattr(group, field, update_data[field])

    db_session.commit()
    return group


def delete(*, db_session, group_id: int):
    """Deletes a group."""
    db_session.query(Group).filter(Group.id == group_id).delete()
    db_session.commit()
