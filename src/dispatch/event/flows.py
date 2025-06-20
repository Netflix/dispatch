import logging

from dispatch.decorators import background_task
from dispatch.event import service as event_service
from dispatch.incident import service as incident_service
from dispatch.case import service as case_service
from dispatch.individual import service as individual_service
from dispatch.event.models import EventUpdate, EventCreateMinimal
from dispatch.auth import service as auth_service

log = logging.getLogger(__name__)


@background_task
def log_incident_event(
    user_email: str,
    incident_id: int,
    event_in: EventCreateMinimal,
    db_session=None,
    organization_slug: str = None,
):
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=user_email, project_id=incident.project.id
    )
    event_in.source = f"Custom event created by {individual.name}"
    event_in.owner = individual.name

    event_service.log_incident_event(
        db_session=db_session,
        incident_id=incident_id,
        individual_id=individual.id,
        **event_in.__dict__,
    )


@background_task
def update_incident_event(
    event_in: EventUpdate,
    db_session=None,
    organization_slug: str = None,
):
    event_service.update_incident_event(
        db_session=db_session,
        event_in=event_in,
    )


@background_task
def delete_incident_event(
    event_uuid: str,
    db_session=None,
    organization_slug: str = None,
):
    event_service.delete_incident_event(
        db_session=db_session,
        uuid=event_uuid,
    )


def export_timeline(
    timeline_filters: dict,
    incident_id: int,
    db_session=None,
    organization_slug: str = None,
):
    try:
        event_service.export_timeline(
            db_session=db_session,
            timeline_filters=timeline_filters,
            incident_id=incident_id,
        )

    except Exception:
        raise


@background_task
def log_case_event(
    user_email: str,
    case_id: int,
    event_in: EventCreateMinimal,
    db_session=None,
    organization_slug: str = None,
):
    case = case_service.get(db_session=db_session, case_id=case_id)
    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=user_email, project_id=case.project.id
    )
    event_in.source = f"Custom event created by {individual.name}"
    event_in.owner = individual.name

    # Get dispatch user by email
    dispatch_user = auth_service.get_by_email(db_session=db_session, email=user_email)
    dispatch_user_id = dispatch_user.id if dispatch_user else None

    event_service.log_case_event(
        db_session=db_session,
        case_id=case_id,
        dispatch_user_id=dispatch_user_id,
        **event_in.__dict__,
    )


@background_task
def update_case_event(
    event_in: EventUpdate,
    db_session=None,
    organization_slug: str = None,
):
    event_service.update_case_event(
        db_session=db_session,
        event_in=event_in,
    )


@background_task
def delete_case_event(
    event_uuid: str,
    db_session=None,
    organization_slug: str = None,
):
    event_service.delete_case_event(
        db_session=db_session,
        uuid=event_uuid,
    )


def export_case_timeline(
    timeline_filters: dict,
    case_id: int,
    db_session=None,
    organization_slug: str = None,
):
    try:
        event_service.export_case_timeline(
            db_session=db_session,
            timeline_filters=timeline_filters,
            case_id=case_id,
        )

    except Exception:
        raise
