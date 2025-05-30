from pydantic import ValidationError

from sqlalchemy.sql.expression import true

from dispatch.project import service as project_service

from .models import (
    IncidentPriority,
    IncidentPriorityCreate,
    IncidentPriorityRead,
    IncidentPriorityUpdate,
)


def get(*, db_session, incident_priority_id: int) -> IncidentPriority | None:
    """Returns an incident priority based on the given priority id."""
    return (
        db_session.query(IncidentPriority)
        .filter(IncidentPriority.id == incident_priority_id)
        .one_or_none()
    )


def get_default(*, db_session, project_id: int):
    """Returns the default incident priority."""
    return (
        db_session.query(IncidentPriority)
        .filter(IncidentPriority.default == true())
        .filter(IncidentPriority.project_id == project_id)
        .one_or_none()
    )


def get_default_or_raise(*, db_session, project_id: int) -> IncidentPriority:
    """Returns the default incident priority or raise a ValidationError if one doesn't exist."""
    incident_priority = get_default(db_session=db_session, project_id=project_id)

    if not incident_priority:
        raise ValidationError(
            [
                {
                    "msg": "No default incident priority defined.",
                    "loc": "incident_priority",
                }
            ]
        )
    return incident_priority


def get_by_name(*, db_session, project_id: int, name: str) -> IncidentPriority | None:
    """Returns an incident priority based on the given priority name."""
    return (
        db_session.query(IncidentPriority)
        .filter(IncidentPriority.name == name)
        .filter(IncidentPriority.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id: int, incident_priority_in=IncidentPriorityRead
) -> IncidentPriority:
    """Returns the incident priority specified or raises ValidationError."""
    incident_priority = get_by_name(
        db_session=db_session, project_id=project_id, name=incident_priority_in.name
    )

    if not incident_priority:
        raise ValidationError(
            [
                {
                    "msg": "Incident priority not found.",
                    "loc": "incident_priority",
                    "incident_priority": incident_priority_in.name,
                }
            ]
        )

    return incident_priority


def get_by_name_or_default(
    *, db_session, project_id: int, incident_priority_in=IncidentPriorityRead
) -> IncidentPriority:
    """Returns a incident priority based on a name or the default if not specified."""
    if incident_priority_in and incident_priority_in.name:
        incident_priority = get_by_name(
            db_session=db_session, project_id=project_id, name=incident_priority_in.name
        )
        if incident_priority:
            return incident_priority
    return get_default_or_raise(db_session=db_session, project_id=project_id)


def get_all(*, db_session, project_id: int = None) -> list[IncidentPriority | None]:
    """Returns all incident priorities."""
    if project_id:
        return db_session.query(IncidentPriority).filter(IncidentPriority.project_id == project_id)
    return db_session.query(IncidentPriority)


def get_all_enabled(*, db_session, project_id: int = None) -> list[IncidentPriority | None]:
    """Returns all enabled incident priorities."""
    if project_id:
        return (
            db_session.query(IncidentPriority)
            .filter(IncidentPriority.project_id == project_id)
            .filter(IncidentPriority.enabled == true())
            .order_by(IncidentPriority.view_order)
        )
    return (
        db_session.query(IncidentPriority)
        .filter(IncidentPriority.enabled == true())
        .order_by(IncidentPriority.view_order)
    )


def create(*, db_session, incident_priority_in: IncidentPriorityCreate) -> IncidentPriority:
    """Creates an incident priority."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=incident_priority_in.project
    )
    incident_priority = IncidentPriority(
        **incident_priority_in.dict(exclude={"project", "color"}), project=project
    )
    if incident_priority_in.color:
        incident_priority.color = incident_priority_in.color

    db_session.add(incident_priority)
    db_session.commit()
    return incident_priority


def update(
    *, db_session, incident_priority: IncidentPriority, incident_priority_in: IncidentPriorityUpdate
) -> IncidentPriority:
    """Updates an incident priority."""
    incident_priority_data = incident_priority.dict()

    update_data = incident_priority_in.dict(exclude_unset=True, exclude={"project", "color"})

    for field in incident_priority_data:
        if field in update_data:
            setattr(incident_priority, field, update_data[field])

    if incident_priority_in.color:
        incident_priority.color = incident_priority_in.color

    db_session.commit()
    return incident_priority


def delete(*, db_session, incident_priority_id: int):
    """Deletes an incident priority."""
    db_session.query(IncidentPriority).filter(IncidentPriority.id == incident_priority_id).delete()
    db_session.commit()
