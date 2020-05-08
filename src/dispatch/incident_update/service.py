from typing import Optional, List

from fastapi.encoders import jsonable_encoder

from .models import IncidentUpdate, IncidentUpdateCreate, IncidentUpdateUpdate


def get(*, db_session, incident_update_id: int) -> Optional[IncidentUpdate]:
    """
    Get an incident update by id.
    """
    return (
        db_session.query(IncidentUpdate)
        .filter(IncidentUpdate.id == incident_update_id)
        .one_or_none()
    )


def get_most_recent_by_incident_id(*, db_session, incident_id: int) -> Optional[IncidentUpdate]:
    """
    Get most recent incident update by id.
    """
    return (
        db_session.query(IncidentUpdate)
        .filter(IncidentUpdate.incident_id == incident_id)
        .order_by(IncidentUpdate.created_at.desc())
        .first()
    )


def get_by_incident_id(*, db_session, incident_id: int) -> List[Optional[IncidentUpdate]]:
    """
    Get incident updates by incident id.
    """
    return db_session.query(IncidentUpdate).filter(IncidentUpdate.incident_id == incident_id)


def get_all(*, db_session):
    """
    Get all incident updates.
    """
    return db_session.query(IncidentUpdate)


def create(*, db_session, incident_update_in: IncidentUpdateCreate) -> IncidentUpdate:
    """
    Create a new incident update.
    """
    incident_update = IncidentUpdate(**incident_update_in.dict())
    db_session.add(incident_update)
    db_session.commit()
    return incident_update


def update(
    *, db_session, incident_update: IncidentUpdate, incident_update_in: IncidentUpdateUpdate
) -> IncidentUpdate:
    """Updates an incident update."""
    incident_update_data = jsonable_encoder(incident_update)
    update_data = incident_update_in.dict(skip_defaults=True)

    for field in incident_update_data:
        if field in update_data:
            setattr(incident_update, field, update_data[field])

    db_session.add(incident_update)
    db_session.commit()
    return incident_update


def delete(*, db_session, incident_update_id: int):
    """Deletes an incident update."""
    db_session.query(IncidentUpdate).filter(IncidentUpdate.id == incident_update_id).delete()
    db_session.commit()
