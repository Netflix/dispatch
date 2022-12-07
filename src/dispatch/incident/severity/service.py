from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.sql.expression import true

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service

from .models import (
    IncidentSeverity,
    IncidentSeverityCreate,
    IncidentSeverityRead,
    IncidentSeverityUpdate,
)


def get(*, db_session, incident_severity_id: int) -> Optional[IncidentSeverity]:
    """Returns an incident severity based on the given severity id."""
    return (
        db_session.query(IncidentSeverity)
        .filter(IncidentSeverity.id == incident_severity_id)
        .one_or_none()
    )


def get_default(*, db_session, project_id: int):
    """Returns the default incident severity."""
    return (
        db_session.query(IncidentSeverity)
        .filter(IncidentSeverity.default == true())
        .filter(IncidentSeverity.project_id == project_id)
        .one_or_none()
    )


def get_default_or_raise(*, db_session, project_id: int) -> IncidentSeverity:
    """Returns the default incident severity or raises a ValidationError if one doesn't exist."""
    incident_severity = get_default(db_session=db_session, project_id=project_id)

    if not incident_severity:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="No default incident severity defined."),
                    loc="incident_severity",
                )
            ],
            model=IncidentSeverityRead,
        )

    return incident_severity


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[IncidentSeverity]:
    """Returns an incident severity based on the given severity name."""
    return (
        db_session.query(IncidentSeverity)
        .filter(IncidentSeverity.name == name)
        .filter(IncidentSeverity.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id: int, incident_severity_in=IncidentSeverityRead
) -> IncidentSeverity:
    """Returns the incident severity specified or raises ValidationError."""
    incident_severity = get_by_name(
        db_session=db_session, project_id=project_id, name=incident_severity_in.name
    )

    if not incident_severity:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Incident severity not found.",
                        incident_severity=incident_severity_in.name,
                    ),
                    loc="incident_severity",
                )
            ],
            model=IncidentSeverityRead,
        )

    return incident_severity


def get_by_name_or_default(
    *, db_session, project_id: int, incident_severity_in=IncidentSeverityRead
) -> IncidentSeverity:
    """Returns an incident severity based on a name or the default if not specified."""
    if incident_severity_in:
        if incident_severity_in.name:
            return get_by_name_or_raise(
                db_session=db_session,
                project_id=project_id,
                incident_severity_in=incident_severity_in,
            )

    return get_default_or_raise(db_session=db_session, project_id=project_id)


def get_all(*, db_session, project_id: int = None) -> List[Optional[IncidentSeverity]]:
    """Returns all incident severities."""
    if project_id:
        return db_session.query(IncidentSeverity).filter(IncidentSeverity.project_id == project_id)

    return db_session.query(IncidentSeverity)


def get_all_enabled(*, db_session, project_id: int = None) -> List[Optional[IncidentSeverity]]:
    """Returns all enabled incident severities."""
    if project_id:
        return (
            db_session.query(IncidentSeverity)
            .filter(IncidentSeverity.project_id == project_id)
            .filter(IncidentSeverity.enabled == true())
            .order_by(IncidentSeverity.view_order)
        )

    return (
        db_session.query(IncidentSeverity)
        .filter(IncidentSeverity.enabled == true())
        .order_by(IncidentSeverity.view_order)
    )


def create(*, db_session, incident_severity_in: IncidentSeverityCreate) -> IncidentSeverity:
    """Creates an incident severity."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=incident_severity_in.project
    )
    incident_severity = IncidentSeverity(
        **incident_severity_in.dict(exclude={"project", "color"}), project=project
    )
    if incident_severity_in.color:
        incident_severity.color = incident_severity_in.color.as_hex()

    db_session.add(incident_severity)
    db_session.commit()

    return incident_severity


def update(
    *, db_session, incident_severity: IncidentSeverity, incident_severity_in: IncidentSeverityUpdate
) -> IncidentSeverity:
    """Updates an incident severity."""
    incident_severity_data = incident_severity.dict()

    update_data = incident_severity_in.dict(skip_defaults=True, exclude={"project", "color"})

    for field in incident_severity_data:
        if field in update_data:
            setattr(incident_severity, field, update_data[field])

    if incident_severity_in.color:
        incident_severity.color = incident_severity_in.color.as_hex()

    db_session.commit()

    return incident_severity


def delete(*, db_session, incident_severity_id: int):
    """Deletes an incident severity."""
    db_session.query(IncidentSeverity).filter(IncidentSeverity.id == incident_severity_id).delete()
    db_session.commit()
