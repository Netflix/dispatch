from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.sql.expression import true

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service

from .models import (
    CaseSeverity,
    CaseSeverityCreate,
    CaseSeverityRead,
    CaseSeverityUpdate,
)


def get(*, db_session, case_severity_id: int) -> Optional[CaseSeverity]:
    """Returns a case severity based on the given severity id."""
    return db_session.query(CaseSeverity).filter(CaseSeverity.id == case_severity_id).one_or_none()


def get_default(*, db_session, project_id: int):
    """Returns the default case severity."""
    return (
        db_session.query(CaseSeverity)
        .filter(CaseSeverity.default == true())
        .filter(CaseSeverity.project_id == project_id)
        .one_or_none()
    )


def get_default_or_raise(*, db_session, project_id: int) -> CaseSeverity:
    """Returns the default case severity or raises a ValidationError if one doesn't exist."""
    case_severity = get_default(db_session=db_session, project_id=project_id)

    if not case_severity:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="No default case severity defined."),
                    loc="case_severity",
                )
            ],
            model=CaseSeverityRead,
        )
    return case_severity


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[CaseSeverity]:
    """Returns a case severity based on the given severity name."""
    return (
        db_session.query(CaseSeverity)
        .filter(CaseSeverity.name == name)
        .filter(CaseSeverity.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id: int, case_severity_in=CaseSeverityRead
) -> CaseSeverity:
    """Returns the case severity specified or raises ValidationError."""
    case_severity = get_by_name(
        db_session=db_session, project_id=project_id, name=case_severity_in.name
    )

    if not case_severity:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Case severity not found.",
                        case_severity=case_severity_in.name,
                    ),
                    loc="case_severity",
                )
            ],
            model=CaseSeverityRead,
        )

    return case_severity


def get_by_name_or_default(
    *, db_session, project_id: int, case_severity_in=CaseSeverityRead
) -> CaseSeverity:
    """Returns a case severity based on a name or the default if not specified."""
    if case_severity_in:
        if case_severity_in.name:
            return get_by_name_or_raise(
                db_session=db_session,
                project_id=project_id,
                case_severity_in=case_severity_in,
            )
    return get_default_or_raise(db_session=db_session, project_id=project_id)


def get_all(*, db_session, project_id: int = None) -> List[Optional[CaseSeverity]]:
    """Returns all case severities."""
    if project_id:
        return db_session.query(CaseSeverity).filter(CaseSeverity.project_id == project_id)
    return db_session.query(CaseSeverity)


def get_all_enabled(*, db_session, project_id: int = None) -> List[Optional[CaseSeverity]]:
    """Returns all enabled case severities."""
    if project_id:
        return (
            db_session.query(CaseSeverity)
            .filter(CaseSeverity.project_id == project_id)
            .filter(CaseSeverity.enabled == true())
        )
    return db_session.query(CaseSeverity).filter(CaseSeverity.enabled == true())


def create(*, db_session, case_severity_in: CaseSeverityCreate) -> CaseSeverity:
    """Creates a case severity."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=case_severity_in.project
    )
    case_severity = CaseSeverity(
        **case_severity_in.dict(exclude={"project", "color"}), project=project
    )
    if case_severity_in.color:
        case_severity.color = case_severity_in.color.as_hex()

    db_session.add(case_severity)
    db_session.commit()
    return case_severity


def update(
    *, db_session, case_severity: CaseSeverity, case_severity_in: CaseSeverityUpdate
) -> CaseSeverity:
    """Updates a case severity."""
    case_severity_data = case_severity.dict()

    update_data = case_severity_in.dict(skip_defaults=True, exclude={"project", "color"})

    for field in case_severity_data:
        if field in update_data:
            setattr(case_severity, field, update_data[field])

    if case_severity_in.color:
        case_severity.color = case_severity_in.color.as_hex()

    db_session.commit()
    return case_severity


def delete(*, db_session, case_severity_id: int):
    """Deletes a case severity."""
    db_session.query(CaseSeverity).filter(CaseSeverity.id == case_severity_id).delete()
    db_session.commit()
