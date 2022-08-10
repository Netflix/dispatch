from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from sqlalchemy.sql.expression import true

from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service

from .models import (
    CasePriority,
    CasePriorityCreate,
    CasePriorityRead,
    CasePriorityUpdate,
)


def get(*, db_session, case_priority_id: int) -> Optional[CasePriority]:
    """Returns a case priority based on the given priority id."""
    return db_session.query(CasePriority).filter(CasePriority.id == case_priority_id).one_or_none()


def get_default(*, db_session, project_id: int):
    """Returns the default case priority."""
    return (
        db_session.query(CasePriority)
        .filter(CasePriority.default == true())
        .filter(CasePriority.project_id == project_id)
        .one_or_none()
    )


def get_default_or_raise(*, db_session, project_id: int) -> CasePriority:
    """Returns the default case priority or raises a ValidationError if one doesn't exist."""
    case_priority = get_default(db_session=db_session, project_id=project_id)

    if not case_priority:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="No default case priority defined."),
                    loc="case_priority",
                )
            ],
            model=CasePriorityRead,
        )
    return case_priority


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[CasePriority]:
    """Returns a case priority based on the given priority name."""
    return (
        db_session.query(CasePriority)
        .filter(CasePriority.name == name)
        .filter(CasePriority.project_id == project_id)
        .one_or_none()
    )


def get_by_name_or_raise(
    *, db_session, project_id: int, case_priority_in=CasePriorityRead
) -> CasePriority:
    """Returns the case priority specified or raises ValidationError."""
    case_priority = get_by_name(
        db_session=db_session, project_id=project_id, name=case_priority_in.name
    )

    if not case_priority:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Case priority not found.",
                        case_priority=case_priority_in.name,
                    ),
                    loc="case_priority",
                )
            ],
            model=CasePriorityRead,
        )

    return case_priority


def get_by_name_or_default(
    *, db_session, project_id: int, case_priority_in=CasePriorityRead
) -> CasePriority:
    """Returns a case priority based on a name or the default if not specified."""
    if case_priority_in:
        if case_priority_in.name:
            return get_by_name_or_raise(
                db_session=db_session,
                project_id=project_id,
                case_priority_in=case_priority_in,
            )
    return get_default_or_raise(db_session=db_session, project_id=project_id)


def get_all(*, db_session, project_id: int = None) -> List[Optional[CasePriority]]:
    """Returns all case priorities."""
    if project_id:
        return db_session.query(CasePriority).filter(CasePriority.project_id == project_id)
    return db_session.query(CasePriority)


def get_all_enabled(*, db_session, project_id: int = None) -> List[Optional[CasePriority]]:
    """Returns all enabled case priorities."""
    if project_id:
        return (
            db_session.query(CasePriority)
            .filter(CasePriority.project_id == project_id)
            .filter(CasePriority.enabled == true())
        )
    return db_session.query(CasePriority).filter(CasePriority.enabled == true())


def create(*, db_session, case_priority_in: CasePriorityCreate) -> CasePriority:
    """Creates a case priority."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=case_priority_in.project
    )
    case_priority = CasePriority(
        **case_priority_in.dict(exclude={"project", "color"}), project=project
    )
    if case_priority_in.color:
        case_priority.color = case_priority_in.color.as_hex()

    db_session.add(case_priority)
    db_session.commit()
    return case_priority


def update(
    *, db_session, case_priority: CasePriority, case_priority_in: CasePriorityUpdate
) -> CasePriority:
    """Updates a case priority."""
    case_priority_data = case_priority.dict()

    update_data = case_priority_in.dict(skip_defaults=True, exclude={"project", "color"})

    for field in case_priority_data:
        if field in update_data:
            setattr(case_priority, field, update_data[field])

    if case_priority_in.color:
        case_priority.color = case_priority_in.color.as_hex()

    db_session.commit()
    return case_priority


def delete(*, db_session, case_priority_id: int):
    """Deletes a case priority."""
    db_session.query(CasePriority).filter(CasePriority.id == case_priority_id).delete()
    db_session.commit()
