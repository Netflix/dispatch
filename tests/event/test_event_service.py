import datetime
import pytest

from uuid import uuid4


def test_get_event(session, event):
    from dispatch.event.service import get

    t_event = get(db_session=session, event_id=event.id)
    assert t_event.id == event.id


def test_get_by_uuid(session, event):
    from dispatch.event.service import get_by_uuid

    t_event = get_by_uuid(db_session=session, uuid=event.uuid)
    assert t_event.uuid == event.uuid


def test_get_by_incident_id(session, event):
    from dispatch.event.service import get_by_incident_id

    t_events = get_by_incident_id(db_session=session, incident_id=event.incident_id).all()
    assert len(t_events) > 1


@pytest.mark.skip()
def test_get_by_incident_id_and_source(session, incident, event):
    from dispatch.event.service import get_by_incident_id_and_source

    t_events = get_by_incident_id_and_source(
        db_session=session, incident_id=incident.id, source=event.source
    )
    assert len(t_events) > 1


@pytest.mark.skip()
def test_get_by_incident_id_and_individual_id(session, incident, individual_contact):
    from dispatch.event.service import test_get_by_incident_id_and_individual_id

    t_events = test_get_by_incident_id_and_individual_id(
        db_session=session, incident_id=incident.id, individual_id=individual_contact.id
    )
    assert len(t_events) > 1


def test_get_all(session, events):
    from dispatch.event.service import get_all

    t_events = get_all(db_session=session).all()
    assert len(t_events) > 1


def test_create(session):
    from dispatch.event.service import create
    from dispatch.event.models import EventCreate

    uuid = uuid4()
    started_at = datetime.datetime.now()
    ended_at = datetime.datetime.now()
    source = "Dispatch event source"
    description = "Dispatch event description"
    event_in = EventCreate(
        uuid=uuid, started_at=started_at, ended_at=ended_at, source=source, description=description
    )
    event = create(db_session=session, event_in=event_in)
    assert source == event.source


@pytest.mark.skip
def test_update(session, event):
    from dispatch.event.event import update
    from dispatch.event.models import EventUpdate

    source = "Source Updated"
    event_in = EventUpdate(source=source)
    event = update(db_session=session, event=event, event_in=event_in)
    assert event.source == source


def test_delete(session, event):
    from dispatch.event.service import delete, get

    delete(db_session=session, event_id=event.id)
    assert not get(db_session=session, event_id=event.id)


def test_log(session, incident):
    from dispatch.event.service import log
    from dispatch.event.models import EventCreate

    source = "Dispatch event source"
    description = "Dispatch event description"
    event = log(db_session=session, source=source, description=description, incident_id=incident.id)
    assert event.source == source
    assert event.incident_id == incident.id
