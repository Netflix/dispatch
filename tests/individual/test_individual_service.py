import pytest


def test_get(session, individual_contact):
    from dispatch.individual.service import get

    t_individual_contact = get(db_session=session, individual_contact_id=individual_contact.id)
    assert t_individual_contact.id == individual_contact.id


def test_get_by_email(session, individual_contact):
    from dispatch.individual.service import get_by_email

    t_individual_contact = get_by_email(db_session=session, email=individual_contact.email)
    assert t_individual_contact.email == individual_contact.email


def test_get_all(session, individual_contact):
    from dispatch.individual.service import get_all

    t_individual_contacts = get_all(db_session=session).all()
    assert len(t_individual_contacts) > 1


def test_get_or_create(session, individual_contact):
    from dispatch.individual.service import create, get_by_email
    from dispatch.individual.models import IndividualContactCreate

    contact = get_by_email(db_session=session, email=individual_contact.email)

    if not contact:
        name = "Joe Smith"
        title = "Engineer"
        email = "jsmith@example.com"
        mobile_phone = "111-111-1111"
        office_phone = "111-111-1111"
        weblink = "https://www.example.com/"

        individual_contact_in = IndividualContactCreate(
            name=name,
            title=title,
            email=email,
            mobile_phone=mobile_phone,
            office_phone=office_phone,
            weblink=weblink,
        )
        contact = create(db_session=session, individual_contact_in=individual_contact_in)

    assert contact


def test_create(session):
    from dispatch.individual.service import create
    from dispatch.individual.models import IndividualContactCreate

    name = "Joe Smith"
    title = "Engineer"
    email = "jsmith@example.com"
    mobile_phone = "111-111-1111"
    office_phone = "111-111-1111"
    weblink = "https://www.example.com/"

    individual_contact_in = IndividualContactCreate(
        name=name,
        title=title,
        email=email,
        mobile_phone=mobile_phone,
        office_phone=office_phone,
        weblink=weblink,
    )
    individual_contact = create(db_session=session, individual_contact_in=individual_contact_in)
    assert individual_contact


def test_delete(session, individual_contact):
    from dispatch.individual.service import delete, get

    delete(db_session=session, individual_contact_id=individual_contact.id)
    assert not get(db_session=session, individual_contact_id=individual_contact.id)
