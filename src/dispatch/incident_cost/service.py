import math

from datetime import datetime

from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from dispatch.config import ANNUAL_COST_EMPLOYEE, BUSINESS_HOURS_YEAR
from dispatch.database.core import SessionLocal
from dispatch.project import service as project_service
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.participant_role.models import ParticipantRoleType

from .models import IncidentCost, IncidentCostCreate, IncidentCostUpdate


HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600


def get(*, db_session, incident_cost_id: int) -> Optional[IncidentCost]:
    """
    Gets an incident cost by its id.
    """
    return db_session.query(IncidentCost).filter(IncidentCost.id == incident_cost_id).one_or_none()


def get_by_incident_cost_type_id(
    *, db_session, incident_cost_type_id: int
) -> List[Optional[IncidentCost]]:
    """
    Gets incident costs by incident cost type id.
    """
    return db_session.query(IncidentCost).filter(
        IncidentCost.incident_cost_type_id == incident_cost_type_id
    )


def get_by_incident_id(*, db_session, incident_id: int) -> List[Optional[IncidentCost]]:
    """
    Gets incident costs by incident id.
    """
    return db_session.query(IncidentCost).filter(IncidentCost.incident_id == incident_id)


def get_by_incident_id_and_incident_cost_type_id(
    *, db_session, incident_id: int, incident_cost_type_id: int
) -> List[Optional[IncidentCost]]:
    """
    Gets incident costs by incident id and incident cost type id.
    """
    return (
        db_session.query(IncidentCost)
        .filter(IncidentCost.incident_id == incident_id)
        .filter(IncidentCost.incident_cost_type_id == incident_cost_type_id)
        .one_or_none()
    )


def get_all(*, db_session) -> List[Optional[IncidentCost]]:
    """
    Gets all incident costs.
    """
    return db_session.query(IncidentCost)


def get_or_create(*, db_session, incident_cost_in: IncidentCostCreate) -> IncidentCost:
    """Gets or creates an incident cost."""
    if incident_cost_in.id:
        incident_cost = get(db_session=db_session, incident_cost_id=incident_cost_in.id)
    else:
        incident_cost = create(db_session=db_session, incident_cost_in=incident_cost_in)

    return incident_cost


def create(*, db_session, incident_cost_in: IncidentCostCreate) -> IncidentCost:
    """
    Creates a new incident cost.
    """
    project = project_service.get_by_name(db_session=db_session, name=incident_cost_in.project.name)
    incident_cost_type = incident_cost_type_service.get_by_name(
        db_session=db_session,
        project_id=project.id,
        incident_cost_type_name=incident_cost_in.incident_cost_type.name,
    )
    incident_cost = IncidentCost(
        **incident_cost_in.dict(exclude={"incident_cost_type", "project"}),
        incident_cost_type=incident_cost_type,
        project=project,
    )
    db_session.add(incident_cost)
    db_session.commit()
    return incident_cost


def update(
    *, db_session, incident_cost: IncidentCost, incident_cost_in: IncidentCostUpdate
) -> IncidentCost:
    """
    Updates an incident cost.
    """
    incident_cost_data = jsonable_encoder(incident_cost)
    update_data = incident_cost_in.dict(skip_defaults=True)

    for field in incident_cost_data:
        if field in update_data:
            setattr(incident_cost, field, update_data[field])

    db_session.add(incident_cost)
    db_session.commit()
    return incident_cost


def delete(*, db_session, incident_cost_id: int):
    """
    Deletes an existing incident cost.
    """
    db_session.query(IncidentCost).filter(IncidentCost.id == incident_cost_id).delete()
    db_session.commit()


def get_engagement_multiplier(participant_role: str):
    """
    Returns an engagement multiplier for a given incident role.
    """
    engagement_mappings = {
        ParticipantRoleType.incident_commander: 1,
        ParticipantRoleType.scribe: 0.75,
        ParticipantRoleType.liaison: 0.75,
        ParticipantRoleType.participant: 0.5,
        ParticipantRoleType.reporter: 0.5,
    }

    return engagement_mappings.get(participant_role)


def calculate_incident_response_cost(
    incident_id: int, db_session: SessionLocal, incident_review=True
):
    """
    Calculates the response cost of a given incident.
    """
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    participants_total_response_time_seconds = 0
    for participant in incident.participants:

        participant_total_roles_time_seconds = 0
        for participant_role in participant.participant_roles:
            # TODO(mvilanova): skip if we did not see activity from the participant in the incident conversation

            participant_role_assumed_at = participant_role.assumed_at

            if incident.status == IncidentStatus.active.value:
                # the incident is still active. we use the current time
                participant_role_renounced_at = datetime.utcnow()
            else:
                # the incident is stable or closed. we use the stable_at time
                participant_role_renounced_at = incident.stable_at

            if participant_role.renounced_at:
                # the participant left the conversation or got assigned another role
                # we use the renounced_at time
                participant_role_renounced_at = participant_role.renounced_at

            # we calculate the time the participant has spent in the incident role
            participant_role_time = participant_role_renounced_at - participant_role_assumed_at

            if participant_role_time.total_seconds() < 0:
                # the participant was added after the incident was marked as stable
                continue

            # we calculate the number of hours the participant has spent in the incident role
            participant_role_time_hours = participant_role_time.total_seconds() / SECONDS_IN_HOUR

            # we make the assumption that participants only spend 8 hours a day working on the incident,
            # if the incident goes past 24hrs
            # TODO(mvilanova): adjust based on incident priority
            if participant_role_time_hours > HOURS_IN_DAY:
                days, hours = divmod(participant_role_time_hours, HOURS_IN_DAY)
                participant_role_time_hours = math.ceil(((days * HOURS_IN_DAY) / 3) + hours)

            # we make the assumption that participants spend more or less time based on their role
            # and we adjust the time spent based on that
            participant_role_time_seconds = int(
                participant_role_time_hours
                * SECONDS_IN_HOUR
                * get_engagement_multiplier(participant_role.role)
            )

            participant_total_roles_time_seconds += participant_role_time_seconds

        participants_total_response_time_seconds += participant_total_roles_time_seconds

    # we calculate the time spent in incident review related activities
    incident_review_hours = 0
    if incident_review:
        num_participants = len(incident.participants)
        incident_review_prep = (
            1  # we make the assumption that it takes an hour to prepare the incident review
        )
        incident_review_meeting = (
            num_participants * 0.5 * 1
        )  # we make the assumption that only half of the incident participants will attend the 1-hour, incident review session
        incident_review_hours = incident_review_prep + incident_review_meeting

    # we calculate and round up the hourly rate
    hourly_rate = math.ceil(ANNUAL_COST_EMPLOYEE / BUSINESS_HOURS_YEAR)

    # we calculate and round up the incident cost
    incident_cost = math.ceil(
        ((participants_total_response_time_seconds / SECONDS_IN_HOUR) + incident_review_hours)
        * hourly_rate
    )

    return incident_cost
