def test_get(session, individual_contact):
    from dispatch.individual.service import get

    t_individual_contact = get(db_session=session, individual_contact_id=individual_contact.id)
    assert t_individual_contact.id == individual_contact.id


def test_get_or_create(session, project, individual_contact):
    from dispatch.individual.service import create, get_by_email_and_project
    from dispatch.individual.models import IndividualContactCreate

    contact = get_by_email_and_project(
        db_session=session, email=individual_contact.email, project_id=project.id
    )

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
            project=project.__dict__,
        )
        contact = create(db_session=session, individual_contact_in=individual_contact_in)

    assert contact


def test_create(session, project):
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
        project=project,
    )
    individual_contact = create(db_session=session, individual_contact_in=individual_contact_in)
    assert individual_contact


def test_update(session, individual_contact):
    from dispatch.individual.service import update
    from dispatch.individual.models import IndividualContactUpdate

    email = "updated@example.com"

    individual_contact_in = IndividualContactUpdate(email=email)
    individual_contact = update(
        db_session=session,
        individual_contact=individual_contact,
        individual_contact_in=individual_contact_in,
    )
    assert individual_contact.email == email


def test_delete(session, individual_contact):
    from dispatch.individual.service import delete, get

    delete(db_session=session, individual_contact_id=individual_contact.id)
    assert not get(db_session=session, individual_contact_id=individual_contact.id)
