import logging

from datetime import datetime, timedelta
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from typing import List, Optional

from dispatch.auth import service as auth_service
from dispatch.case.priority import service as case_priority_service
from dispatch.case.severity import service as case_severity_service
from dispatch.case.type import service as case_type_service
from dispatch.data.source import service as source_service
from dispatch.event import service as event_service
from dispatch.exceptions import NotFoundError
from dispatch.incident import service as incident_service
from dispatch.project import service as project_service
from dispatch.tag import service as tag_service

from .enums import CaseStatus
from .models import (
    Case,
    CaseCreate,
    CaseRead,
    CaseUpdate,
    AssocCaseCaseType,
    AssocCaseCaseSeverity,
    AssocCaseCasePriority,
)


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


# def get_all_last_x_hours_by_status(
#     *, db_session, project_id: int, status: str, hours: int
# ) -> List[Optional[Case]]:
#     """Returns all cases of a given status in the last x hours."""
#     now = datetime.utcnow()
#
#     if status == CaseStatus.active:
#         return (
#             db_session.query(Case)
#             .filter(Case.project_id == project_id)
#             .filter(Case.status == CaseStatus.active)
#             .filter(Case.created_at >= now - timedelta(hours=hours))
#             .all()
#         )
#
#     if status == CaseStatus.stable:
#         return (
#             db_session.query(Case)
#             .filter(Case.project_id == project_id)
#             .filter(Case.status == CaseStatus.stable)
#             .filter(Case.stable_at >= now - timedelta(hours=hours))
#             .all()
#         )
#
#     if status == CaseStatus.closed:
#         return (
#             db_session.query(Case)
#             .filter(Case.project_id == project_id)
#             .filter(Case.status == CaseStatus.closed)
#             .filter(Case.closed_at >= now - timedelta(hours=hours))
#             .all()
#         )


def create(*, db_session, case_in: CaseCreate) -> Case:
    """Creates a new case."""
    project = project_service.get_by_name_or_default(
        db_session=db_session, project_in=case_in.project
    )

    tag_objs = []
    for t in case_in.tags:
        tag_objs.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    case = Case(
        title=case_in.title,
        description=case_in.description,
        project=project,
        status=case_in.status,
        tags=tag_objs,
    )

    if case_in.assignee:
        case.assignee = auth_service.get_by_email(
            db_session=db_session, email=case_in.assignee.email
        )

    if case_in.source:
        case.source = source_service.get_by_name(
            db_session=db_session, project_id=project.id, name=case_in.source.name
        )

    case_type = case_type_service.get_by_name_or_default(
        db_session=db_session, project_id=project.id, case_type_in=case_in.case_type
    )
    case.case_types.append(AssocCaseCaseType(case_type))

    case.visibility = case_type.visibility
    if case_in.visibility:
        case.visibility = case_in.visibility

    case_severity = case_severity_service.get_by_name_or_default(
        db_session=db_session, project_id=project.id, case_severity_in=case_in.case_severity
    )
    case.case_severities.append(AssocCaseCaseSeverity(case_severity))

    case_priority = case_priority_service.get_by_name_or_default(
        db_session=db_session, project_id=project.id, case_priority_in=case_in.case_priority
    )
    case.case_priorities.append(AssocCaseCasePriority(case_priority))

    db_session.add(case)
    db_session.commit()

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Case created",
        case_id=case.id,
    )

    return case


def update(*, db_session, case: Case, case_in: CaseUpdate) -> Case:
    """Updates an existing case."""
    update_data = case_in.dict(
        skip_defaults=True,
        exclude={
            "assignee",
            "case_priority",
            "case_severity",
            "case_type",
            "duplicates",
            "incidents",
            "project",
            "source",
            "status",
            "tags",
            "visibility",
        },
    )

    for field in update_data.keys():
        setattr(case, field, update_data[field])

    case.assignee = auth_service.get_by_email(db_session=db_session, email=case_in.assignee.email)

    if case_in.case_type:
        if case.case_type.name != case_in.case_type.name:
            case_type = case_type_service.get_by_name(
                db_session=db_session,
                project_id=case.project.id,
                name=case_in.case_type.name,
            )
            case.case_types.append(AssocCaseCaseType(case_type))

    if case_in.case_severity:
        if case.case_severity.name != case_in.case_severity.name:
            case_severity = case_severity_service.get_by_name(
                db_session=db_session,
                project_id=case.project.id,
                name=case_in.case_severity.name,
            )
            case.case_severities.append(AssocCaseCaseSeverity(case_severity))

    if case_in.case_priority:
        if case.case_priority.name != case_in.case_priority.name:
            case_priority = case_priority_service.get_by_name(
                db_session=db_session,
                project_id=case.project.id,
                name=case_in.case_priority.name,
            )
            case.case_priorities.append(AssocCaseCasePriority(case_priority))

    if case_in.source:
        if case.source.name != case_in.source.name:
            case.source = source_service.get_by_name(
                db_session=db_session, project_id=case.project.id, name=case_in.source.name
            )

    tags = []
    for t in case_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))
    case.tags = tags

    duplicates = []
    for d in case_in.duplicates:
        duplicates.append(get(db_session=db_session, case_id=d.id))
    case.duplicates = duplicates

    incidents = []
    for i in case_in.incidents:
        incidents.append(incident_service.get(db_session=db_session, incident_id=i.id))
    case.incidents = incidents

    case.status = case_in.status
    case.visibility = case_in.visibility

    db_session.commit()

    return case


def delete(*, db_session, case_id: int):
    """Deletes an existing case."""
    db_session.query(Case).filter(Case.id == case_id).delete()
    db_session.commit()
