from typing import Optional

from .models import Group


def get(*, db_session, group_id: int) -> Optional[Group]:
    return db_session.query(Group).filter(Group.id == group_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Group]:
    return db_session.query(Group).filter(Group.resource_id == resource_id).one()


def get_by_resource_type(*, db_session, resource_type: str) -> Optional[Group]:
    return db_session.query(Group).filter(Group.resource_type == resource_type).one()


def get_by_incident_id_and_resource_type(
    *, db_session, incident_id: str, resource_type: str
) -> Optional[Group]:
    return (
        db_session.query(Group)
        .filter(Group.incident_id == incident_id)
        .filter(Group.resource_type == resource_type)
        .one()
    )


def get_all(*, db_session):
    return db_session.query(Group)


def create(*, db_session, **kwargs) -> Group:
    group = Group(**kwargs)
    db_session.add(group)
    db_session.commit()
    return group
