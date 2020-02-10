from typing import Optional

from .models import Storage


def get(*, db_session, ticket_id: int) -> Optional[Storage]:
    return db_session.query(Storage).filter(Storage.id == ticket_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Storage]:
    return db_session.query(Storage).filter(Storage.resource_id == resource_id).one()


def get_by_resource_type(*, db_session, resource_type: str) -> Optional[Storage]:
    return db_session.query(Storage).filter(Storage.resource_type == resource_type).one()


def get_all(*, db_session):
    return db_session.query(Storage)


def create(*, db_session, **kwargs) -> Storage:
    contact = Storage(**kwargs)
    db_session.add(contact)
    db_session.commit()
    return contact
