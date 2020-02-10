from typing import Optional

from .models import IncidentPriority


def get(*, db_session, incident_priority_id: int) -> Optional[IncidentPriority]:
    return (
        db_session.query(IncidentPriority).filter(IncidentPriority.id == incident_priority_id).one()
    )


def get_by_name(*, db_session, name: str) -> Optional[IncidentPriority]:
    return db_session.query(IncidentPriority).filter(IncidentPriority.name == name).one()


def get_all(*, db_session):
    return db_session.query(IncidentPriority)


def create(*, db_session, **kwargs) -> IncidentPriority:
    contact = IncidentPriority(**kwargs)
    db_session.add(contact)
    db_session.commit()
    return contact
