def test_get(session, conference):
    from dispatch.conference.service import get

    test_conference = get(db_session=session, conference_id=conference.id)
    assert test_conference.id == conference.id
    assert test_conference.conference_challenge == conference.conference_challenge


def test_get_by_resource_id(session, conference):
    from dispatch.conference.service import get_by_resource_id

    test_conference = get_by_resource_id(db_session=session, resource_id=conference.resource_id)

    assert test_conference.resource_id == conference.resource_id
    assert test_conference.conference_challenge == conference.conference_challenge


def test_get_by_incident_id(session, conference):
    from dispatch.conference.service import get_by_incident_id

    test_conference = get_by_incident_id(db_session=session, incident_id=conference.incident.id)

    assert test_conference.incident.id == conference.incident.id
    assert test_conference.conference_challenge == conference.conference_challenge


def test_get_all(session, conferences):
    """The test should not rely on the conferences created earlier, to pass.
    Therefore, we pass "conferences" as an argument, to manually create several in the DB.
    """
    from dispatch.conference.service import get_all

    test_conferences = get_all(db_session=session).all()
    assert test_conferences


def test_create(session):
    from dispatch.conference.service import create
    from dispatch.conference.models import ConferenceCreate

    resource_id = "000000"
    resource_type = "resourcetype"
    weblink = "https://www.example.com"
    conference_id = "12345"
    conference_challenge = "a0v0a0v9a"

    conference_in = ConferenceCreate(
        resource_id=resource_id,
        resource_type=resource_type,
        weblink=weblink,
        conference_id=conference_id,
        conference_challenge=conference_challenge,
    )
    conference = create(db_session=session, conference_in=conference_in)
    assert conference
    assert conference.resource_id == "000000"
    assert conference.resource_type == "resourcetype"
    assert conference.weblink == "https://www.example.com"
    assert conference.conference_id == "12345"
    assert conference.conference_challenge == "a0v0a0v9a"
