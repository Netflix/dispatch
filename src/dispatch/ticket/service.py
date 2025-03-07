from typing import Optional

from sqlalchemy.orm import Session

from .models import Ticket, TicketCreate


def get(*, db_session: Session, ticket_id: int) -> Optional[Ticket]:
    """Fetch a ticket by its ticket id."""
    return db_session.query(Ticket).filter(Ticket.id == ticket_id).one()


def get_by_resource_id(*, db_session: Session, resource_id: str) -> Optional[Ticket]:
    """Fetch a ticket by its resource id."""
    return db_session.query(Ticket).filter(Ticket.resource_id == resource_id).one()


def get_by_weblink(*, db_session: Session, weblink: str) -> Optional[Ticket]:
    """Fetch a ticket by its weblink."""
    return db_session.query(Ticket).filter(Ticket.weblink == weblink).one_or_none()


def get_or_create_by_weblink(*, db_session: Session, weblink: str, resource_type: str) -> Ticket:
    """Fetch a ticket or creating a new one."""
    ticket = get_by_weblink(db_session=db_session, weblink=weblink)
    if not ticket:
        ticket = Ticket(weblink=weblink, resource_type=resource_type)
        db_session.add(ticket)
        db_session.commit()
    return ticket


def get_all(*, db_session: Session):
    """Fetches all tickets."""
    return db_session.query(Ticket)


def create(*, db_session: Session, ticket_in: TicketCreate) -> Ticket:
    """Creates a ticket."""
    ticket = Ticket(**ticket_in.dict())
    db_session.add(ticket)
    db_session.commit()
    return ticket


def delete(*, db_session: Session, ticket_id: int):
    """Deletes a ticket."""
    db_session.query(Ticket).filter(Ticket.id == ticket_id).delete()
    db_session.commit()
