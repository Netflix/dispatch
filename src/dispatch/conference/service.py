from typing import Optional

from .models import Conference, ConferenceCreate


def get(*, db_session, conference_id: int) -> Optional[Conference]:
    """Fetch a conference by it's `conference_id`."""
    return db_session.query(Conference).filter(Conference.id == conference_id).one()


def get_by_resource_id(*, db_session, resource_id: str) -> Optional[Conference]:
    """Fetch a conference by it's `resource_id`."""
    return db_session.query(Conference).filter(Conference.resource_id == resource_id).one_or_none()


def get_by_incident_id(*, db_session, incident_id: str) -> Optional[Conference]:
    """Fetch a conference by it's associated `incident_id`."""
    return db_session.query(Conference).filter(Conference.incident_id == incident_id).one()


def get_all(*, db_session):
    """Fetch all conferences."""
    return db_session.query(Conference)


def create(*, db_session, conference_in: ConferenceCreate) -> Conference:
    """Create a new conference."""
    conference = Conference(**conference_in.dict())
    db_session.add(conference)
    db_session.commit()
    db_session.flush(conference)
    return conference
