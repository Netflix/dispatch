from datetime import datetime, timedelta, timezone
import logging
import math
from typing import List, Optional

from dispatch.database.core import SessionLocal
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import Incident
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.incident_cost_type.models import IncidentCostTypeRead
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantRead
from dispatch.participant_activity import service as participant_activity_service
from dispatch.participant_activity.models import ParticipantActivityCreate
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service

from .models import IncidentCost, IncidentCostCreate, IncidentCostUpdate


HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600
log = logging.getLogger(__name__)


def get(*, db_session, incident_cost_id: int) -> Optional[IncidentCost]:
    """Gets an incident cost by its id."""
    return db_session.query(IncidentCost).filter(IncidentCost.id == incident_cost_id).one_or_none()


def get_by_incident_id(*, db_session, incident_id: int) -> List[Optional[IncidentCost]]:
    """Gets incident costs by their incident id."""
    return db_session.query(IncidentCost).filter(IncidentCost.incident_id == incident_id)


def get_by_incident_id_and_incident_cost_type_id(
    *, db_session, incident_id: int, incident_cost_type_id: int
) -> List[Optional[IncidentCost]]:
    """Gets incident costs by their incident id and incident cost type id."""
    return (
        db_session.query(IncidentCost)
        .filter(IncidentCost.incident_id == incident_id)
        .filter(IncidentCost.incident_cost_type_id == incident_cost_type_id)
        .one_or_none()
    )


def get_all(*, db_session) -> List[Optional[IncidentCost]]:
    """Gets all incident costs."""
    return db_session.query(IncidentCost)


def get_or_create(*, db_session, incident_cost_in: IncidentCostCreate) -> IncidentCost:
    """Gets or creates an incident cost."""
    if incident_cost_in.id:
        incident_cost = get(db_session=db_session, incident_cost_id=incident_cost_in.id)
    else:
        incident_cost = create(db_session=db_session, incident_cost_in=incident_cost_in)

    return incident_cost


def create(*, db_session, incident_cost_in: IncidentCostCreate) -> IncidentCost:
    """Creates a new incident cost."""
    incident_cost_type = incident_cost_type_service.get(
        db_session=db_session, incident_cost_type_id=incident_cost_in.incident_cost_type.id
    )
    incident_cost = IncidentCost(
        **incident_cost_in.dict(exclude={"incident_cost_type", "project"}),
        incident_cost_type=incident_cost_type,
        project=incident_cost_type.project,
    )
    db_session.add(incident_cost)
    db_session.commit()

    return incident_cost


def update(
    *, db_session, incident_cost: IncidentCost, incident_cost_in: IncidentCostUpdate
) -> IncidentCost:
    """Updates an incident cost."""
    incident_cost_data = incident_cost.dict()
    update_data = incident_cost_in.dict(skip_defaults=True)

    for field in incident_cost_data:
        if field in update_data:
            setattr(incident_cost, field, update_data[field])

    db_session.commit()
    return incident_cost


def delete(*, db_session, incident_cost_id: int):
    """Deletes an existing incident cost."""
    db_session.query(IncidentCost).filter(IncidentCost.id == incident_cost_id).delete()
    db_session.commit()


def get_engagement_multiplier(participant_role: str):
    """Returns an engagement multiplier for a given incident role."""
    engagement_mappings = {
        ParticipantRoleType.incident_commander: 1,
        ParticipantRoleType.scribe: 0.75,
        ParticipantRoleType.liaison: 0.75,
        ParticipantRoleType.participant: 0.5,
        ParticipantRoleType.reporter: 0.5,
        # ParticipantRoleType.observer: 0, # NOTE: set to 0. It's not used, as we don't calculate cost for participants with observer role
    }

    return engagement_mappings.get(participant_role)


def get_incident_review_hours(incident: Incident) -> int:
    """Calculate the time spent in incident review related activities."""
    num_participants = len(incident.participants)
    incident_review_prep = (
        1  # we make the assumption that it takes an hour to prepare the incident review
    )
    incident_review_meeting = (
        num_participants * 0.5 * 1
    )  # we make the assumption that only half of the incident participants will attend the 1-hour, incident review session
    return incident_review_prep + incident_review_meeting


def calculate_incident_response_cost_with_cost_model(
    incident: Incident, db_session: SessionLocal
) -> int:
    """Calculates the cost of an incident using the incident's cost model."""

    participants_total_response_time_seconds = 0

    # Get the cost model. Iterate through all the listed activities we want to record.
    for activity in incident.cost_model.activities:
        plugin_instance = plugin_service.get_active_instance_by_slug(
            db_session=db_session,
            slug=activity.plugin_event.plugin.slug,
            project_id=incident.project.id,
        )
        if not plugin_instance:
            log.warning(
                f"Cannot fetch cost model activity. Its associated plugin {activity.plugin_event.plugin.title} is not enabled."
            )
            continue

        oldest = "0"
        response_cost_type = incident_cost_type_service.get_default(
            db_session=db_session, project_id=incident.project.id
        )
        incident_response_cost = get_by_incident_id_and_incident_cost_type_id(
            db_session=db_session,
            incident_id=incident.id,
            incident_cost_type_id=response_cost_type.id,
        )
        if incident_response_cost:
            oldest = incident_response_cost.updated_at.replace(tzinfo=timezone.utc).timestamp()

        # Array of sorted (timestamp, user_id) tuples.
        incident_events = plugin_instance.instance.fetch_incident_events(
            db_session=db_session,
            subject=incident,
            plugin_event_id=activity.plugin_event.id,
            oldest=oldest,
        )

        for ts, user_id in incident_events:
            participant = participant_service.get_by_incident_id_and_conversation_id(
                db_session=db_session,
                incident_id=incident.id,
                user_conversation_id=user_id,
            )
            if not participant:
                log.warning("Cannot resolve participant.")
                continue

            activity_in = ParticipantActivityCreate(
                plugin_event=activity.plugin_event,
                started_at=ts,
                ended_at=ts + timedelta(seconds=activity.response_time_seconds),
                participant=ParticipantRead(id=participant.id),
                incident=incident,
            )

            if participant_response_time := participant_activity_service.create_or_update(
                db_session=db_session, activity_in=activity_in
            ):
                participants_total_response_time_seconds += (
                    participant_response_time.total_seconds()
                )

    # Calculate and round up the hourly rate.
    hourly_rate = math.ceil(
        incident.project.annual_employee_cost / incident.project.business_year_hours
    )
    additional_incident_cost = math.ceil(
        (participants_total_response_time_seconds / SECONDS_IN_HOUR) * hourly_rate
    )
    return incident.total_cost + additional_incident_cost


def calculate_incident_response_cost_with_classic_model(incident: Incident, incident_review=True):
    participants_total_response_time_seconds = 0
    for participant in incident.participants:
        participant_total_roles_time_seconds = 0

        for participant_role in participant.participant_roles:
            if participant_role.role == ParticipantRoleType.observer:
                # skip calculating cost for participants with the observer role
                continue

            if participant_role.activity == 0:
                # skip calculating cost for roles that have no activity
                continue

            participant_role_assumed_at = participant_role.assumed_at
            # we set the renounced_at default time to the current time
            participant_role_renounced_at = datetime.utcnow()

            if incident.status == IncidentStatus.active:
                if participant_role.renounced_at:
                    # the participant left the conversation or got assigned another role
                    # we use the role's renounced_at time
                    participant_role_renounced_at = participant_role.renounced_at
            else:
                # we set the renounced_at default time to the stable_at time if the stable_at time exists
                if incident.stable_at:
                    participant_role_renounced_at = incident.stable_at

                if participant_role.renounced_at:
                    # the participant left the conversation or got assigned another role
                    if participant_role.renounced_at < participant_role_renounced_at:
                        # we use the role's renounced_at time if it happened before the
                        # incident was marked as stable or closed
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
    if incident_review:
        incident_review_hours = get_incident_review_hours(incident)
    # we calculate and round up the hourly rate
    hourly_rate = math.ceil(
        incident.project.annual_employee_cost / incident.project.business_year_hours
    )

    # we calculate and round up the incident cost
    return math.ceil(
        ((participants_total_response_time_seconds / SECONDS_IN_HOUR) + incident_review_hours)
        * hourly_rate
    )


def calculate_incident_response_cost(
    incident_id: int, db_session: SessionLocal, incident_review=True
) -> int:
    """Calculates the response cost of a given incident."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    if not incident:
        log.warning(f"Incident with id {incident_id} not found.")
        return 0
    if incident.cost_model and incident.cost_model.enabled:
        log.debug(f"Calculating {incident.name} incident cost with model {incident.cost_model}.")
        return calculate_incident_response_cost_with_cost_model(
            incident=incident, db_session=db_session
        )
    else:
        log.debug("No incident cost model found. Defaulting to classic incident cost model.")
        return calculate_incident_response_cost_with_classic_model(
            incident=incident, incident_review=incident_review
        )


def update_incident_response_cost(incident_id: int, db_session: SessionLocal) -> int:
    """Updates the response cost of a given incident."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    response_cost_type = incident_cost_type_service.get_default(
        db_session=db_session, project_id=incident.project.id
    )

    if response_cost_type is None:
        log.warning(
            f"A default cost type for response cost doesn't exist in the {incident.project.name} project and organization {incident.project.organization.name}. Response costs for incident {incident.name} won't be calculated."
        )
        return 0

    incident_response_cost = get_by_incident_id_and_incident_cost_type_id(
        db_session=db_session,
        incident_id=incident.id,
        incident_cost_type_id=response_cost_type.id,
    )
    if incident_response_cost is None:
        # we create the response cost if it doesn't exist
        incident_cost_type = IncidentCostTypeRead.from_orm(response_cost_type)
        incident_cost_in = IncidentCostCreate(
            incident_cost_type=incident_cost_type, project=incident.project
        )
        incident_response_cost = create(db_session=db_session, incident_cost_in=incident_cost_in)
    amount = calculate_incident_response_cost(incident_id=incident.id, db_session=db_session)
    # we don't need to update the cost amount if it hasn't changed
    if incident_response_cost.amount == amount:
        return incident_response_cost.amount

    # we save the new incident cost amount
    incident_response_cost.amount = amount
    incident.incident_costs.append(incident_response_cost)
    db_session.add(incident)
    db_session.commit()

    return incident_response_cost.amount
