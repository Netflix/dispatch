from pydantic import ValidationError

from sqlalchemy.sql.expression import true

from dispatch.project import service as project_service

from .models import (
    IncidentSeverity,
    IncidentSeverityCreate,
    IncidentSeverityRead,
    IncidentSeverityUpdate,
)


def get(*, db_session, incident_severity_id: int) -> IncidentSeverity | None:
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
        raise ValidationError.from_exception_data(
            "IncidentSeverityRead",
            [
                {
                    "type": "value_error",
                    "loc": ("incident_severity",),
                    "input": None,
                    "msg": "No default incident severity defined.",
                    "ctx": {"error": ValueError("No default incident severity defined.")},
                }
            ],
        )

    return incident_severity


def get_by_name(*, db_session, project_id: int, name: str) -> IncidentSeverity | None:
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
                {
                    "msg": "Incident severity not found.",
                    "loc": ("incident_severity",),
                    "type": "value_error.not_found",
                    "incident_severity": incident_severity_in.name,
                }
            ]
        )

    return incident_severity


def get_by_name_or_default(
    *, db_session, project_id: int, incident_severity_in=IncidentSeverityRead
) -> IncidentSeverity:
    """Returns an incident severity based on a name or the default if not specified."""
    if incident_severity_in and incident_severity_in.name:
        incident_severity = get_by_name(
            db_session=db_session, project_id=project_id, name=incident_severity_in.name
        )
        if incident_severity:
            return incident_severity
    return get_default_or_raise(db_session=db_session, project_id=project_id)


def get_all(*, db_session, project_id: int = None) -> list[IncidentSeverity | None]:
    """Returns all incident severities."""
    if project_id:
        return db_session.query(IncidentSeverity).filter(IncidentSeverity.project_id == project_id)

    return db_session.query(IncidentSeverity).all()


def get_all_enabled(*, db_session, project_id: int = None) -> list[IncidentSeverity | None]:
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
        incident_severity.color = incident_severity_in.color

    db_session.add(incident_severity)
    db_session.commit()

    return incident_severity


def update(
    *, db_session, incident_severity: IncidentSeverity, incident_severity_in: IncidentSeverityUpdate
) -> IncidentSeverity:
    """Updates an incident severity."""
    incident_severity_data = incident_severity.dict()

    update_data = incident_severity_in.dict(exclude_unset=True, exclude={"project", "color"})

    for field in incident_severity_data:
        if field in update_data:
            setattr(incident_severity, field, update_data[field])

    if incident_severity_in.color:
        incident_severity.color = incident_severity_in.color

    db_session.commit()

    return incident_severity


def delete(*, db_session, incident_severity_id: int):
    """Deletes an incident severity."""
    db_session.query(IncidentSeverity).filter(IncidentSeverity.id == incident_severity_id).delete()
    db_session.commit()
