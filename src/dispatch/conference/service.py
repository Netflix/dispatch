from typing import Optional

from .models import Conference


def get(*, db_session, conference_id: int) -> Optional[Conference]:
    return db_session.query(Conference).filter(Conference.id == conference_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Conference]:
    return db_session.query(Conference).filter(Conference.resource_id == resource_id).one_or_none()


def get_by_resource_type(*, db_session, resource_type: str) -> Optional[Conference]:
    return (
        db_session.query(Conference).filter(Conference.resource_type == resource_type).one_or_none()
    )


def get_by_channel_id(db_session, conference_id: str) -> Optional[Conference]:
    return (
        db_session.query(Conference).filter(Conference.conference_id == conference_id).one_or_none()
    )


def get_all(*, db_session):
    return db_session.query(Conference)


def create(*, db_session, **kwargs) -> Conference:
    contact = Conference(**kwargs)
    db_session.add(contact)
    db_session.commit()
    db_session.flush(contact)

    return contact
