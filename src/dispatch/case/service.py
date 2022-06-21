import logging

from datetime import datetime, timedelta
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from typing import List, Optional

# from dispatch.case_priority import service as case_priority_service
# from dispatch.case_type import service as case_type_service
from dispatch.database.core import SessionLocal
from dispatch.event import service as event_service
from dispatch.exceptions import NotFoundError
from dispatch.project import service as project_service
from dispatch.tag import service as tag_service

from .enums import CaseStatus
from .models import Case, CaseCreate, CaseRead, CaseUpdate


log = logging.getLogger(__name__)


def get(*, db_session, case_id: int) -> Optional[Case]:
    """Returns an case based on the given id."""
    return db_session.query(Case).filter(Case.id == case_id).first()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[Case]:
    """Returns an case based on the given name."""
    return (
        db_session.query(Case)
        .filter(Case.project_id == project_id)
        .filter(Case.name == name)
        .first()
    )


def get_by_name_or_raise(*, db_session, project_id: int, case_in: CaseRead) -> Case:
    """Returns an case based on a given name or raises ValidationError"""
    case = get_by_name(db_session=db_session, project_id=project_id, name=case_in.name)

    if not case:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Case not found.",
                        query=case_in.name,
                    ),
                    loc="case",
                )
            ],
            model=CaseRead,
        )
    return case


def get_all(*, db_session, project_id: int) -> List[Optional[Case]]:
    """Returns all cases."""
    return db_session.query(Case).filter(Case.project_id == project_id)


def get_all_by_status(*, db_session, project_id: int, status: str) -> List[Optional[Case]]:
    """Returns all cases based on a given status."""
    return (
        db_session.query(Case)
        .filter(Case.project_id == project_id)
        .filter(Case.status == status)
        .all()
    )


def get_all_last_x_hours_by_status(
    *, db_session, project_id: int, status: str, hours: int
) -> List[Optional[Case]]:
    """Returns all cases of a given status in the last x hours."""
    now = datetime.utcnow()

    if status == CaseStatus.active:
        return (
            db_session.query(Case)
            .filter(Case.project_id == project_id)
            .filter(Case.status == CaseStatus.active)
            .filter(Case.created_at >= now - timedelta(hours=hours))
            .all()
        )

    if status == CaseStatus.stable:
        return (
            db_session.query(Case)
            .filter(Case.project_id == project_id)
            .filter(Case.status == CaseStatus.stable)
            .filter(Case.stable_at >= now - timedelta(hours=hours))
            .all()
        )

    if status == CaseStatus.closed:
        return (
            db_session.query(Case)
            .filter(Case.project_id == project_id)
            .filter(Case.status == CaseStatus.closed)
            .filter(Case.closed_at >= now - timedelta(hours=hours))
            .all()
        )


def create(*, db_session, case_in: CaseCreate) -> Case:
    """Creates a new case."""
    project = project_service.get_by_name_or_default(
        db_session=db_session, project_in=case_in.project
    )

    # case_type = case_type_service.get_by_name_or_default(
    #     db_session=db_session, project_id=project.id, case_type_in=case_in.case_type
    # )
    #
    # case_priority = case_priority_service.get_by_name_or_default(
    #     db_session=db_session,
    #     project_id=project.id,
    #     case_priority_in=case_in.case_priority,
    # )

    # if not case_in.visibility:
    #     visibility = case_type.visibility
    # else:
    #     visibility = case_in.visibility

    tag_objs = []
    for t in case_in.tags:
        tag_objs.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    # NOTE: add reporter, and resolve and add assignee
    case = Case(
        # case_priority=case_priority,
        # case_type=case_type,
        description=case_in.description,
        project=project,
        status=case_in.status,
        tags=tag_objs,
        title=case_in.title,
        # visibility=visibility,
    )
    db_session.add(case)
    db_session.commit()

    event_service.log(
        db_session=db_session,
        source="Dispatch Core App",
        description="Case created",
        case_id=case.id,
    )

    return case


def update(*, db_session, case: Case, case_in: CaseUpdate) -> Case:
    """Updates an existing case."""
    # case_type = case_type_service.get_by_name_or_default(
    #     db_session=db_session,
    #     project_id=case.project.id,
    #     case_type_in=case_in.case_type,
    # )
    #
    # case_priority = case_priority_service.get_by_name_or_default(
    #     db_session=db_session,
    #     project_id=case.project.id,
    #     case_priority_in=case_in.case_priority,
    # )

    tags = []
    for t in case_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    duplicates = []
    for d in case_in.duplicates:
        duplicates.append(get(db_session=db_session, case_id=d.id))

    update_data = case_in.dict(
        skip_defaults=True,
        exclude={
            # "case_priority",
            # "case_type",
            "commander",
            "duplicates",
            "project",
            "reporter",
            "status",
            "tags",
            "visibility",
        },
    )

    for field in update_data.keys():
        setattr(case, field, update_data[field])

    # case.case_priority = case_priority
    # case.case_type = case_type
    case.duplicates = duplicates
    case.status = case_in.status
    case.tags = tags
    case.visibility = case_in.visibility

    db_session.commit()

    return case


def delete(*, db_session, case_id: int):
    """Deletes an existing case."""
    db_session.query(Case).filter(Case.id == case_id).delete()
    db_session.commit()
