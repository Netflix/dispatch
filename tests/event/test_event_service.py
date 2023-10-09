import datetime
from uuid import uuid4
from dispatch.enums import EventType


def test_get(session, event):
    from dispatch.event.service import get

    t_event = get(db_session=session, event_id=event.id)
    assert t_event.id == event.id


def test_get_by_incident_id(session, event):
    from dispatch.event.service import get_by_incident_id

    t_events = get_by_incident_id(db_session=session, incident_id=event.incident_id).all()
    assert t_events


def test_get_all(session, events):
    from dispatch.event.service import get_all

    t_events = get_all(db_session=session).all()
    assert t_events


def test_create(session):
    from dispatch.event.service import create
    from dispatch.event.models import EventCreate

    uuid = uuid4()
    started_at = datetime.datetime.now()
    ended_at = datetime.datetime.now()
    source = "Dispatch event source"
    description = "Dispatch event description"
    event_in = EventCreate(
        uuid=uuid,
        started_at=started_at,
        ended_at=ended_at,
        source=source,
        description=description,
        type=EventType.other,
    )
    event = create(db_session=session, event_in=event_in)
    assert source == event.source


def test_update(session, event):
    from dispatch.event.service import update
    from dispatch.event.models import EventUpdate

    uuid = uuid4()
    started_at = datetime.datetime.now()
    ended_at = datetime.datetime.now()
    source = "Dispatch event source updated"
    description = "Dispatch event description"
    event_in = EventUpdate(
        uuid=uuid,
        started_at=started_at,
        ended_at=ended_at,
        source=source,
        description=description,
        type=EventType.other,
    )
    event = update(db_session=session, event=event, event_in=event_in)
    assert event.source == source


def test_delete(session, event):
    from dispatch.event.service import delete, get

    delete(db_session=session, event_id=event.id)
    assert not get(db_session=session, event_id=event.id)


def test_log_incident_event(session, incident):
    from dispatch.event.service import log_incident_event

    source = "Dispatch event source"
    description = "Dispatch event description"
    event = log_incident_event(
        db_session=session, source=source, description=description, incident_id=incident.id
    )
    assert event.source == source
    assert event.incident_id == incident.id


def test_log_case_event(session, case):
    from dispatch.event.service import log_case_event

    source = "Dispatch event source"
    description = "Dispatch event description"
    event = log_case_event(
        db_session=session, source=source, description=description, case_id=case.id
    )
    assert event.source == source
    assert event.case_id == case.id
