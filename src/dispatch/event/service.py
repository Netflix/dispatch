import datetime
from uuid import uuid4

from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from sqlalchemy.dialects.postgresql import UUID

from .models import Event, EventCreate, EventUpdate


def get(*, db_session, event_id: int) -> Optional[Event]:
    """
    Get an event by id.
    """
    return db_session.query(Event).filter(Event.id == event_id).one_or_none()


def get_by_uuid(*, db_session, uuid: UUID) -> Optional[Event]:
    """
    Get an event by uuid.
    """
    return db_session.query(Event).filter(Event.uuid == uuid).one_or_none()


def get_by_incident_id(*, db_session, incident_id: int) -> List[Optional[Event]]:
    """
    Get events by incident id.
    """
    return db_session.query(Event).filter(Event.incident_id == incident_id)


def get_by_incident_id_and_source(
    *, db_session, incident_id: int, source: str
) -> List[Optional[Event]]:
    """
    Get events by incident id and source.
    """
    return (
        db_session.query(Event)
        .filter(Event.incident_id == incident_id)
        .filter(Event.source == source)
    )


def get_by_incident_id_and_individual_id(
    *, db_session, incident_id: int, individual_id: int
) -> List[Optional[Event]]:
    """
    Get events by incident id and individual id.
    """
    return (
        db_session.query(Event)
        .filter(Event.incident_id == incident_id)
        .filter(Event.source == individual_id)
    )


def get_all(*, db_session) -> List[Optional[Event]]:
    """
    Get all events.
    """
    return db_session.query(Event)


def create(*, db_session, event_in: EventCreate) -> Event:
    """
    Create a new event.
    """
    event = Event(**event_in.dict())
    db_session.add(event)
    db_session.commit()
    return event


def update(*, db_session, event: Event, event_in: EventUpdate) -> Event:
    """
    Updates an event.
    """
    event_data = jsonable_encoder(event)
    update_data = event_in.dict(skip_defaults=True)

    for field in event_data:
        if field in update_data:
            setattr(event, field, update_data[field])

    db_session.add(event)
    db_session.commit()
    return event


def delete(*, db_session, event_id: int):
    """
    Deletes an event
    """
    event = db_session.query(Event).filter(Event.id == event_id).first()
    db_session.delete(event)
    db_session.commit()


def log(
    *,
    db_session,
    source: str,
    description: str,
    started_at: datetime = None,
    ended_at: datetime = None
) -> Event:
    """
    Logs an event
    """
    uuid = uuid4()

    if not started_at:
        started_at = datetime.datetime.now()

    event_in = EventCreate(
        uuid=uuid, started_at=started_at, ended_at=ended_at, source=source, description=description
    )
    event = create(db_session=db_session, event_in=event_in)
    return event
