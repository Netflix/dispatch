import math
from datetime import datetime
from typing import List, Optional, Tuple

from fastapi.encoders import jsonable_encoder

from dispatch.config import (
    ANNUAL_COST_EMPLOYEE,
    BUSINESS_HOURS_YEAR,
    ENV,
    HOURS_IN_DAY,
    INCIDENT_ONCALL_PLUGIN_SLUG,
    SECONDS_IN_HOUR,
)
from dispatch.database import SessionLocal
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_priority.models import IncidentPriorityType
from dispatch.incident_type import service as incident_type_service
from dispatch.individual import service as individual_service
from dispatch.participant import service as participant_service
from dispatch.participant_role import service as participant_role_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.base import plugins

from .enums import IncidentStatus
from .models import Incident, IncidentUpdate


def resolve_incident_commander_email(
    db_session: SessionLocal,
    reporter_email: str,
    incident_type: str,
    incident_priority: str,
    incident_name: str,
    incident_title: str,
    incident_description: str,
):
    """Resolve the correct incident commander email based on given parameters."""
    if incident_priority == IncidentPriorityType.info:
        return reporter_email
    elif ENV == "test":
        return reporter_email

    commander_service = incident_type_service.get_by_name(db_session=db_session, name=incident_type).commander_service

    p = plugins.get(commander_service.type)

    # page for high priority incidents
    # we could do this at the end but it seems pretty important...
    if incident_priority == IncidentPriorityType.high:
        p.page(
            service_id=commander_service.external_id,
            incident_name=incident_name,
            incident_title=incident_title,
            incident_description=incident_description,
        )

    return p.get(service_id=commander_service.external_id)


def get(*, db_session, incident_id: str) -> Optional[Incident]:
    return db_session.query(Incident).filter(Incident.id == incident_id).first()


def get_by_name(*, db_session, incident_name: str) -> Optional[Incident]:
    return db_session.query(Incident).filter(Incident.name == incident_name).first()


def get_all(*, db_session) -> Optional[Tuple]:
    return db_session.query(Incident)


def get_all_by_status(
    *, db_session, status: IncidentStatus, skip=0, limit=100
) -> List[Optional[Incident]]:
    return (
        db_session.query(Incident).filter(Incident.status == status).offset(skip).limit(limit).all()
    )


def create(
    *,
    db_session,
    incident_priority: str,
    incident_type: str,
    reporter_email: str,
    title: str,
    status: str,
    description: str,
) -> Incident:
    participants = []

    # TODO should some of this logic be in the incident_create_flow_instead? (kglisson)
    incident_priority = incident_priority_service.get_by_name(
        db_session=db_session, name=incident_priority["name"]
    )

    incident_type = incident_type_service.get_by_name(
        db_session=db_session, name=incident_type["name"]
    )

    commander_email = resolve_incident_commander_email(
        db_session, reporter_email, incident_type.name, incident_priority.name, "", title, description
    )

    commander_info = individual_service.resolve_user_by_email(commander_email)

    incident_commander_role = participant_role_service.create(
        db_session=db_session, role=ParticipantRoleType.incident_commander
    )

    commander_participant = participant_service.create(
        db_session=db_session, participant_role=[incident_commander_role]
    )

    commander = individual_service.get_or_create(
        db_session=db_session,
        email=commander_info["email"],
        name=commander_info["fullname"],
        weblink=commander_info["weblink"],
    )

    incident_reporter_role = participant_role_service.create(
        db_session=db_session, role=ParticipantRoleType.reporter
    )

    if reporter_email == commander_email:
        commander_participant.participant_role.append(incident_reporter_role)
    else:
        reporter_participant = participant_service.create(
            db_session=db_session, participant_role=[incident_reporter_role]
        )
        reporter_info = individual_service.resolve_user_by_email(reporter_email)
        reporter = individual_service.get_or_create(
            db_session=db_session,
            email=reporter_info["email"],
            name=reporter_info["fullname"],
            weblink=commander_info["weblink"],
        )
        reporter.participant.append(reporter_participant)
        db_session.add(reporter)
        participants.append(reporter_participant)

    participants.append(commander_participant)
    incident = Incident(
        title=title,
        description=description,
        status=status,
        incident_priority=incident_priority,
        incident_type=incident_type,
        participants=participants,
    )

    commander.participant.append(commander_participant)
    db_session.add(commander)
    db_session.add(incident)
    db_session.commit()
    return incident


def update(*, db_session, incident: Incident, incident_in: IncidentUpdate) -> Incident:
    incident_data = jsonable_encoder(incident)

    incident_priority = incident_priority_service.get_by_name(
        db_session=db_session, name=incident_in.incident_priority.name
    )

    incident_type = incident_type_service.get_by_name(
        db_session=db_session, name=incident_in.incident_type.name
    )

    # TODO find code to add command as participant incident.commander = commander
    # commander = individual_service.get_by_email(
    #    db_session=db_session, email=incident_in.commander.email
    # )

    update_data = incident_in.dict(
        skip_defaults=True, exclude={"incident_type", "incident_priority", "commander"}
    )

    for field in incident_data:
        if field in update_data:
            setattr(incident, field, update_data[field])

    incident.incident_priority = incident_priority
    incident.incident_type = incident_type

    db_session.add(incident)
    db_session.commit()
    return incident


def delete(*, db_session, incident_id: int):
    # TODO: When deleting, respect referential integrity here in the code. Or add cascading deletes
    # in models.py.
    db_session.query(Incident).filter(Incident.id == incident_id).delete()
    db_session.commit()


def calculate_cost(incident_id: int, db_session: SessionLocal, incident_review=False):
    """Calculates the incident cost."""
    # we ge the incident
    incident = get(db_session=db_session, incident_id=incident_id)

    participants_active_hours = 0
    for participant in incident.participants:
        participant_active_at = participant.active_at
        participant_inactive_at = (
            participant.inactive_at if participant.inactive_at else datetime.utcnow()
        )

        participant_active_time = participant_inactive_at - participant_active_at
        participant_active_hours = participant_active_time.total_seconds() / SECONDS_IN_HOUR

        # we assume that participants only spend ~10 hours/day working on the incident if the incident goes past 24hrs
        if participant_active_hours > HOURS_IN_DAY:
            days, hours = divmod(participant_active_hours, HOURS_IN_DAY)
            participant_active_hours = math.ceil((days * HOURS_IN_DAY * 0.4) + hours)

        participants_active_hours += participant_active_hours

    num_participants = len(incident.participants)

    # we calculate the number of hours spent responding per person using the 25/50/25 rule,
    # where 25% of participants get a full share, 50% get a half share, and 25% get a quarter share
    response_hours_full_share = num_participants * 0.25 * participants_active_hours
    response_hours_half_share = num_participants * 0.5 * participants_active_hours * 0.5
    response_hours_quarter_share = num_participants * 0.25 * participants_active_hours * 0.25
    response_hours = (
        response_hours_full_share + response_hours_half_share + response_hours_quarter_share
    )

    # we calculate the number of hours spent in incident review related activities
    incident_review_hours = 0
    if incident_review:
        incident_review_prep = 1
        incident_review_meeting = num_participants * 0.5 * 1
        incident_review_hours = incident_review_prep + incident_review_meeting

    # we calculate and round up the hourly rate
    hourly_rate = math.ceil(ANNUAL_COST_EMPLOYEE / BUSINESS_HOURS_YEAR)

    # we calculate, round up, and format the incident cost
    incident_cost = f"{math.ceil((response_hours + incident_review_hours) * hourly_rate):.2f}"
    return incident_cost
