from typing import Optional

from .models import Ticket


def get(*, db_session, ticket_id: int) -> Optional[Ticket]:
    return db_session.query(Ticket).filter(Ticket.id == ticket_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Ticket]:
    return db_session.query(Ticket).filter(Ticket.resource_id == resource_id).one()


def get_by_resource_type(*, db_session, resource_type: str) -> Optional[Ticket]:
    return db_session.query(Ticket).filter(Ticket.resource_type == resource_type).one()


def get_all(*, db_session):
    return db_session.query(Ticket)


def create(*, db_session, **kwargs) -> Ticket:
    contact = Ticket(**kwargs)
    db_session.add(contact)
    db_session.commit()
    return contact
