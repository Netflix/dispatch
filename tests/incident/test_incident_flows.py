import pytest


def test_incident_create_flow(incident, session):
    from dispatch.incident.flows import incident_create_flow

    incident_create_flow(incident_id=incident.id, db_session=session)

    assert incident.commander.name
    assert incident.conference.conference_challenge
    assert incident.conference.weblink
    assert incident.conversation.weblink
    assert incident.description
    assert incident.incident_priority.name
    assert incident.incident_type.name
    assert incident.name
    assert incident.status
    assert incident.storage.weblink
    assert incident.ticket.weblink
    assert incident.title
    assert incident.visibility
