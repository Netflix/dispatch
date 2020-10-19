from typing import Optional

from .models import Ticket, TicketCreate


def get(*, db_session, ticket_id: int) -> Optional[Ticket]:
    """Fetch a ticket by it's `ticket_id`."""
    return db_session.query(Ticket).filter(Ticket.id == ticket_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Ticket]:
    """Fetch a ticket by it's `resource_id`."""
    return db_session.query(Ticket).filter(Ticket.resource_id == resource_id).one()


def get_by_weblink(*, db_session, weblink: str) -> Optional[Ticket]:
    """Fetch a ticket by it's `weblink`."""
    return db_session.query(Ticket).filter(Ticket.weblink == weblink).one_or_none()


def get_by_resource_type(*, db_session, resource_type: str) -> Optional[Ticket]:
    """Fetch a ticket based on it's `resource_type`."""
    return db_session.query(Ticket).filter(Ticket.resource_type == resource_type).one()


def get_or_create_by_weblink(*, db_session, weblink: str, resource_type: str) -> Ticket:
    """Fetch a ticket or creating a new one."""
    ticket = get_by_weblink(db_session=db_session, weblink=weblink)
    if not ticket:
        ticket = Ticket(weblink=weblink, resource_type=resource_type)
        db_session.add(ticket)
        db_session.commit()
    return ticket


def get_all(*, db_session):
    """Fetches all tickets."""
    return db_session.query(Ticket)


def create(*, db_session, ticket_in: TicketCreate) -> Ticket:
    """Creates a new ticket."""
    ticket = Ticket(**ticket_in.dict())
    db_session.add(ticket)
    db_session.commit()

    return ticket
