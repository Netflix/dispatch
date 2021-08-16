def test_get(session, ticket):
    from dispatch.ticket.service import get

    t_ticket = get(db_session=session, ticket_id=ticket.id)
    assert t_ticket.id == ticket.id


def test_get_by_resource_id(session, ticket):
    from dispatch.ticket.service import get_by_resource_id

    t_ticket = get_by_resource_id(db_session=session, resource_id=ticket.resource_id)
    assert t_ticket.resource_id == ticket.resource_id


def test_get_all(session, tickets):
    from dispatch.ticket.service import get_all

    t_tickets = get_all(db_session=session).all()
    assert t_tickets


def test_create(session, incident_type, incident_priority, individual_contact):
    from dispatch.ticket.service import create
    from dispatch.ticket.models import TicketCreate

    resource_id = "XXX"
    resource_type = "XXX"
    weblink = "https://example.com/"

    ticket_in = TicketCreate(
        resource_id=resource_id,
        resource_type=resource_type,
        weblink=weblink,
    )
    ticket = create(db_session=session, ticket_in=ticket_in)

    assert ticket
