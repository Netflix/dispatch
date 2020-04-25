import pytest


def test_create_conference(session):
    from dispatch.conference.service import create
    from dispatch.conference.models import ConferenceCreate

    name = "fakename"
    resource_id = "000000"
    resource_type = "resourcetype"
    weblink = "https://www.example.com"
    conference_id = "12345"
    conference_challenge = "a0v0a0v9a"

    conference_in = ConferenceCreate(
        name=name,
        resource_id=resource_id,
        resource_type=resource_type,
        weblink=weblink,
        conference_id=conference_id,
        conference_challenge=conference_challenge,
    )
    conference = create(db_session=session, conference_in=conference_in)
    assert conference


def test_get_conference(session, conference):
    from dispatch.conference.service import get

    test_conference = get(db_session=session, conference_id=conference.id)
    assert test_conference.id == conference.id
