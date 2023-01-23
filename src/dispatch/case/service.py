import logging

from datetime import datetime, timedelta

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from typing import List, Optional

from dispatch.auth import service as auth_service
from dispatch.auth.models import DispatchUser
from dispatch.case.priority import service as case_priority_service
from dispatch.case.severity import service as case_severity_service
from dispatch.case.type import service as case_type_service
from dispatch.event import service as event_service
from dispatch.exceptions import NotFoundError
from dispatch.incident import service as incident_service
from dispatch.project import service as project_service
from dispatch.service import flows as service_flows
from dispatch.tag import service as tag_service

from .enums import CaseStatus
from .models import (
    Case,
    CaseCreate,
    CaseRead,
    CaseUpdate,
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


def get_all_last_x_hours_by_status(
    *, db_session, project_id: int, status: str, hours: int
) -> List[Optional[Case]]:
    """Returns all cases of a given status in the last x hours."""
    now = datetime.utcnow()

    if status == CaseStatus.new:
        return (
            db_session.query(Case)
            .filter(Case.project_id == project_id)
            .filter(Case.status == CaseStatus.new)
            .filter(Case.created_at >= now - timedelta(hours=hours))
            .all()
        )

    if status == CaseStatus.triage:
        return (
            db_session.query(Case)
            .filter(Case.project_id == project_id)
            .filter(Case.status == CaseStatus.triage)
            .filter(Case.triage_at >= now - timedelta(hours=hours))
            .all()
        )

    if status == CaseStatus.escalated:
        return (
            db_session.query(Case)
            .filter(Case.project_id == project_id)
            .filter(Case.status == CaseStatus.escalated)
            .filter(Case.escalated_at >= now - timedelta(hours=hours))
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


def create(*, db_session, case_in: CaseCreate, current_user: DispatchUser = None) -> Case:
    """Creates a new case."""
    project = project_service.get_by_name_or_default(
        db_session=db_session, project_in=case_in.project
    )

    tag_objs = []
    for t in case_in.tags:
        tag_objs.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    # TODO(mvilanova): allow to provide related cases and incidents, and duplicated cases

    case = Case(
        title=case_in.title,
        description=case_in.description,
        project=project,
        status=case_in.status,
        tags=tag_objs,
    )

    case_type = case_type_service.get_by_name_or_default(
        db_session=db_session, project_id=project.id, case_type_in=case_in.case_type
    )
    case.case_type = case_type

    case.visibility = case_type.visibility
    if case_in.visibility:
        case.visibility = case_in.visibility

    if case_in.assignee:
        # we assign the case to the assignee provided
        assignee_email_adddress = case_in.assignee.email
    else:
        if case_type.oncall_service:
            # we assign the case to the oncall person for the given case type
            assignee_email_adddress = service_flows.resolve_oncall(
                service=case_type.oncall_service, db_session=db_session
            )
        else:
            # we assign the case to the current user
            if current_user:
                assignee_email_adddress = current_user.email

    case.assignee = auth_service.get_by_email(db_session=db_session, email=assignee_email_adddress)

    case_severity = case_severity_service.get_by_name_or_default(
        db_session=db_session, project_id=project.id, case_severity_in=case_in.case_severity
    )
    case.case_severity = case_severity

    case_priority = case_priority_service.get_by_name_or_default(
        db_session=db_session, project_id=project.id, case_priority_in=case_in.case_priority
    )
    case.case_priority = case_priority

    db_session.add(case)
    db_session.commit()

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Case created",
        case_id=case.id,
    )

    return case


def update(*, db_session, case: Case, case_in: CaseUpdate, current_user: DispatchUser) -> Case:
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
            "related",
            "status",
            "tags",
            "visibility",
        },
    )

    for field in update_data.keys():
        setattr(case, field, update_data[field])

    if case_in.assignee:
        if case.assignee.email != case_in.assignee.email:
            case_assignee = auth_service.get_by_email(
                db_session=db_session, email=case_in.assignee.email
            )
            if case_assignee:
                case.assignee = case_assignee

                event_service.log_case_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description=f"Case assigned to {case_in.assignee.email} by {current_user.email}",
                    dispatch_user_id=current_user.id,
                    case_id=case.id,
                )
            else:
                log.warning(f"Dispatch user with email address {case_in.assignee.email} not found.")

    if case_in.case_type:
        if case.case_type.name != case_in.case_type.name:
            case_type = case_type_service.get_by_name(
                db_session=db_session,
                project_id=case.project.id,
                name=case_in.case_type.name,
            )
            if case_type:
                case.case_type = case_type

                event_service.log_case_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description=(
                        f"Case type changed to {case_in.case_type.name.lower()} "
                        f"by {current_user.email}"
                    ),
                    dispatch_user_id=current_user.id,
                    case_id=case.id,
                )
            else:
                log.warning(f"Case type with name {case_in.case_type.name.lower()} not found.")

    if case_in.case_severity:
        if case.case_severity.name != case_in.case_severity.name:
            case_severity = case_severity_service.get_by_name(
                db_session=db_session,
                project_id=case.project.id,
                name=case_in.case_severity.name,
            )
            if case_severity:
                case.case_severity = case_severity

                event_service.log_case_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description=(
                        f"Case severity changed to {case_in.case_severity.name.lower()} "
                        f"by {current_user.email}"
                    ),
                    dispatch_user_id=current_user.id,
                    case_id=case.id,
                )
            else:
                log.warning(
                    f"Case severity with name {case_in.case_severity.name.lower()} not found."
                )

    if case_in.case_priority:
        if case.case_priority.name != case_in.case_priority.name:
            case_priority = case_priority_service.get_by_name(
                db_session=db_session,
                project_id=case.project.id,
                name=case_in.case_priority.name,
            )
            if case_priority:
                case.case_priority = case_priority

                event_service.log_case_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description=(
                        f"Case priority changed to {case_in.case_priority.name.lower()} "
                        f"by {current_user.email}"
                    ),
                    dispatch_user_id=current_user.id,
                    case_id=case.id,
                )
            else:
                log.warning(
                    f"Case priority with name {case_in.case_priority.name.lower()} not found."
                )

    if case.status != case_in.status:
        case.status = case_in.status

        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=(
                f"Case status changed to {case_in.status.lower()} " f"by {current_user.email}"
            ),
            dispatch_user_id=current_user.id,
            case_id=case.id,
        )

    if case.visibility != case_in.visibility:
        case.visibility = case_in.visibility

        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=(
                f"Case visibility changed to {case_in.visibility.lower()} "
                f"by {current_user.email}"
            ),
            dispatch_user_id=current_user.id,
            case_id=case.id,
        )

    tags = []
    for t in case_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))
    case.tags = tags

    related = []
    for r in case_in.related:
        related.append(get(db_session=db_session, case_id=r.id))
    case.related = related

    duplicates = []
    for d in case_in.duplicates:
        duplicates.append(get(db_session=db_session, case_id=d.id))
    case.duplicates = duplicates

    incidents = []
    for i in case_in.incidents:
        incidents.append(incident_service.get(db_session=db_session, incident_id=i.id))
    case.incidents = incidents

    db_session.commit()

    return case


def delete(*, db_session, case_id: int):
    """Deletes an existing case."""
    db_session.query(Case).filter(Case.id == case_id).delete()
    db_session.commit()
