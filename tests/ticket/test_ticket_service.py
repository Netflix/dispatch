import pytest


def test_get_ticket(session, ticket):
    from dispatch.ticket.service import get

    t_ticket = get(db_session=session, ticket_id=ticket.id)
    assert t_ticket.id == ticket.id


def test_get_by_resource_id(session, ticket):
    from dispatch.ticket.service import get_by_resource_id

    t_ticket = get_by_resource_id(db_session=session, resource_id=ticket.resource_id)
    assert t_ticket.resource_id == ticket.resource_id


def test_get_by_resource_type(session, ticket):
    from dispatch.ticket.service import get_by_resource_type

    t_ticket = get_by_resource_type(db_session=session, resource_type=ticket.resource_type)
    assert t_ticket.resource_type == ticket.resource_type


def test_get_all(session):
    from dispatch.ticket.service import get_all

    t_ticket = get_all(db_session=session).all()

    assert len(t_ticket) > 1


def test_create(session, incident_type, incident_priority, individual_contact):
    from dispatch.ticket.service import create
    from dispatch.ticket.models import TicketCreate

    resource_id = "XXX"
    resource_type = "XXX"
    weblink = "https://example.com/"

    ticket_in = TicketCreate(resource_id=resource_id, resource_type=resource_type, weblink=weblink)
    ticket = create(db_session=session, ticket_in=ticket_in)

    assert ticket
