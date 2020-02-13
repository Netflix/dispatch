from typing import Optional

from .models import Ticket, TicketCreate


def get(*, db_session, ticket_id: int) -> Optional[Ticket]:
    """Returns a ticket based on a given id."""
    return db_session.query(Ticket).filter(Ticket.id == ticket_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Ticket]:
    """Returns a ticket based on the given resource id."""
    return db_session.query(Ticket).filter(Ticket.resource_id == resource_id).one()


def get_by_resource_type(*, db_session, resource_type: str) -> Optional[Ticket]:
    """Returns a ticket based on the given resource type."""
    return db_session.query(Ticket).filter(Ticket.resource_type == resource_type).one()


def get_all(*, db_session):
    """Returns all tickets."""
    return db_session.query(Ticket)


def create(*, db_session, ticket_in: TicketCreate) -> Ticket:
    """Creates a new ticket."""
    ticket = Ticket(**ticket_in.dict())
    db_session.add(ticket)
    db_session.commit()

    return ticket
