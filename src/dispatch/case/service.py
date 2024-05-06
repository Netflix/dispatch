import logging

from datetime import datetime, timedelta

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from dispatch.auth.models import DispatchUser
from dispatch.case.priority import service as case_priority_service
from dispatch.case.severity import service as case_severity_service
from dispatch.case.type import service as case_type_service
from dispatch.event import service as event_service
from dispatch.exceptions import NotFoundError
from dispatch.incident import service as incident_service
from dispatch.participant.models import Participant
from dispatch.participant import flows as participant_flows
from dispatch.participant_role.models import ParticipantRoleType
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
    """Creates a new case.

    Returns:
        The created case.

    Raises:
        ValidationError: If the case type does not have a conversation target and the case is not being created with a dedicated channel, the case will not be created.
    """
    project = project_service.get_by_name_or_default(
        db_session=db_session, project_in=case_in.project
    )

    tag_objs = []
    for t in case_in.tags:
        tag_objs.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    # TODO(mvilanova): allow to provide related cases and incidents, and duplicated cases
    case_type = case_type_service.get_by_name_or_default(
        db_session=db_session, project_id=project.id, case_type_in=case_in.case_type
    )

    # Cases with dedicated channels do not require a conversation target.
    if not case_in.dedicated_channel:
        if not case_type or not case_type.conversation_target:
            raise ValueError(
                f"Cases without dedicated channels require a conversation target. Case type with name {case_in.case_type.name} does not have a conversation target. The case will not be created."
            )

    case = Case(
        title=case_in.title,
        description=case_in.description,
        project=project,
        status=case_in.status,
        dedicated_channel=case_in.dedicated_channel,
        tags=tag_objs,
        case_type=case_type,
    )

    case.visibility = case_type.visibility
    if case_in.visibility:
        case.visibility = case_in.visibility

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
        details={
            "title": case.title,
            "description": case.description,
            "type": case.case_type.name,
            "severity": case.case_severity.name,
            "priority": case.case_priority.name,
            "status": case.status,
            "visibility": case.visibility,
        },
        case_id=case.id,
    )

    assignee_email = None
    if case_in.assignee:
        # we assign the case to the assignee provided
        assignee_email = case_in.assignee.individual.email
    elif case_type.oncall_service:
        # we assign the case to the oncall person for the given case type
        assignee_email = service_flows.resolve_oncall(
            service=case_type.oncall_service, db_session=db_session
        )
    elif current_user:
        # we fall back to assign the case to the current user
        assignee_email = current_user.email

    # add assignee
    if assignee_email:
        participant_flows.add_participant(
            assignee_email,
            case,
            db_session,
            role=ParticipantRoleType.assignee,
        )

    # add reporter
    if case_in.reporter:
        participant_flows.add_participant(
            case_in.reporter.individual.email,
            case,
            db_session,
            role=ParticipantRoleType.reporter,
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
            "reporter",
            "status",
            "tags",
            "visibility",
        },
    )

    for field in update_data.keys():
        setattr(case, field, update_data[field])

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
                f"Case status changed to {case_in.status.lower()} by {current_user.email}"
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


def get_participants(
    *, db_session: Session, case_id: int, minimal: bool = False
) -> list[Participant]:
    """Returns a list of participants based on the given case id."""
    if minimal:
        case = (
            db_session.query(Case)
            .join(Case.participants)  # Use join for minimal
            .filter(Case.id == case_id)
            .first()
        )
    else:
        case = (
            db_session.query(Case)
            .options(joinedload(Case.participants))  # Use joinedload for full objects
            .filter(Case.id == case_id)
            .first()
        )

    return [] if case is None or case.participants is None else case.participants
