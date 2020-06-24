from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql.expression import true

from .models import IncidentPriority, IncidentPriorityCreate, IncidentPriorityUpdate


def get(*, db_session, incident_priority_id: int) -> Optional[IncidentPriority]:
    """Returns an incident priority based on the given priority id."""
    return (
        db_session.query(IncidentPriority)
        .filter(IncidentPriority.id == incident_priority_id)
        .one_or_none()
    )


def get_default(*, db_session):
    """Returns the current default incident_priority."""
    return (
        db_session.query(IncidentPriority).filter(IncidentPriority.default == true()).one_or_none()
    )


def get_by_name(*, db_session, name: str) -> Optional[IncidentPriority]:
    """Returns an incident priority based on the given priority name."""
    return db_session.query(IncidentPriority).filter(IncidentPriority.name == name).one_or_none()


def get_by_slug(*, db_session, slug: str) -> Optional[IncidentPriority]:
    """Returns an incident priority based on the given type slug."""
    return db_session.query(IncidentPriority).filter(IncidentPriority.slug == slug).one_or_none()


def get_all(*, db_session) -> List[Optional[IncidentPriority]]:
    """Returns all incident priorities."""
    return db_session.query(IncidentPriority)


def create(*, db_session, incident_priority_in: IncidentPriorityCreate) -> IncidentPriority:
    """Creates an incident priority."""
    incident_priority = IncidentPriority(**incident_priority_in.dict())
    db_session.add(incident_priority)
    db_session.commit()
    return incident_priority


def update(
    *, db_session, incident_priority: IncidentPriority, incident_priority_in: IncidentPriorityUpdate
) -> IncidentPriority:
    """Updates an incident priority."""
    incident_priority_data = jsonable_encoder(incident_priority)
    update_data = incident_priority_in.dict(skip_defaults=True)

    for field in incident_priority_data:
        if field in update_data:
            setattr(incident_priority, field, update_data[field])

    db_session.add(incident_priority)
    db_session.commit()
    return incident_priority


def delete(*, db_session, incident_priority_id: int):
    """Deletes an incident priority."""
    db_session.query(IncidentPriority).filter(IncidentPriority.id == incident_priority_id).delete()
    db_session.commit()
