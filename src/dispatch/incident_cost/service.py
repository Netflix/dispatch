from datetime import datetime, timedelta, timezone
import logging
import math
from typing import List, Optional

from dispatch.database.core import SessionLocal
from dispatch.cost_model.models import CostModelActivity
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import Incident
from dispatch.incident.type.models import IncidentType
from dispatch.incident_cost_type import service as incident_cost_type_service
from dispatch.incident_cost_type.models import IncidentCostTypeRead
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantRead
from dispatch.participant_activity import service as participant_activity_service
from dispatch.participant_activity.models import ParticipantActivityCreate
from dispatch.participant_role.models import ParticipantRoleType, ParticipantRole
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
    return db_session.query(IncidentCost).filter(IncidentCost.incident_id == incident_id).all()


def get_by_incident_id_and_incident_cost_type_id(
    *, db_session, incident_id: int, incident_cost_type_id: int
) -> Optional[IncidentCost]:
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


def get_or_create(
    *, db_session, incident_cost_in: IncidentCostCreate | IncidentCostUpdate
) -> IncidentCost:
    """Gets or creates an incident cost object."""
    if type(incident_cost_in) is IncidentCostUpdate and incident_cost_in.id:
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


def get_hourly_rate(project) -> int:
    """Calculates and rounds up the employee hourly rate within a project."""
    return math.ceil(project.annual_employee_cost / project.business_year_hours)


def update_incident_response_cost_for_incident_type(
    db_session, incident_type: IncidentType
) -> None:
    """Calculate the response cost of all non-closed incidents associated with this incident type."""
    incidents = incident_service.get_all_open_by_incident_type(
        db_session=db_session, incident_type_id=incident_type.id
    )
    for incident in incidents:
        update_incident_response_cost(incident_id=incident.id, db_session=db_session)


def calculate_response_cost(
    hourly_rate, total_response_time_seconds, incident_review_hours=0
) -> int:
    """Calculates and rounds up the incident response cost."""
    return math.ceil(
        ((total_response_time_seconds / SECONDS_IN_HOUR) + incident_review_hours) * hourly_rate
    )


def get_default_incident_response_cost(
    incident: Incident, db_session: SessionLocal
) -> Optional[IncidentCost]:
    response_cost_type = incident_cost_type_service.get_default(
        db_session=db_session, project_id=incident.project.id
    )

    if not response_cost_type:
        log.warning(
            f"A default cost type for response cost doesn't exist in the {incident.project.name} project and organization {incident.project.organization.name}. Response costs for incident {incident.name} won't be calculated."
        )
        return None

    return get_by_incident_id_and_incident_cost_type_id(
        db_session=db_session,
        incident_id=incident.id,
        incident_cost_type_id=response_cost_type.id,
    )


def get_or_create_default_incident_response_cost(
    incident: Incident, db_session: SessionLocal
) -> Optional[IncidentCost]:
    """Gets or creates the default incident cost for an incident.

    The default incident cost is the cost associated with the participant effort in an incident's response.
    """
    response_cost_type = incident_cost_type_service.get_default(
        db_session=db_session, project_id=incident.project.id
    )

    if not response_cost_type:
        log.warning(
            f"A default cost type for response cost doesn't exist in the {incident.project.name} project and organization {incident.project.organization.name}. Response costs for incident {incident.name} won't be calculated."
        )
        return None

    incident_response_cost = get_by_incident_id_and_incident_cost_type_id(
        db_session=db_session,
        incident_id=incident.id,
        incident_cost_type_id=response_cost_type.id,
    )

    if not incident_response_cost:
        # we create the response cost if it doesn't exist
        incident_cost_type = IncidentCostTypeRead.from_orm(response_cost_type)
        incident_cost_in = IncidentCostCreate(
            incident_cost_type=incident_cost_type, project=incident.project
        )
        incident_response_cost = create(db_session=db_session, incident_cost_in=incident_cost_in)
        incident.incident_costs.append(incident_response_cost)
        db_session.add(incident)
        db_session.commit()

    return incident_response_cost


def fetch_incident_events(
    incident: Incident, activity: CostModelActivity, oldest: str, db_session: SessionLocal
) -> List[Optional[tuple[datetime.timestamp, str]]]:
    plugin_instance = plugin_service.get_active_instance_by_slug(
        db_session=db_session,
        slug=activity.plugin_event.plugin.slug,
        project_id=incident.project.id,
    )
    if not plugin_instance:
        log.warning(
            f"Cannot fetch cost model activity. Its associated plugin {activity.plugin_event.plugin.title} is not enabled."
        )
        return []

    # Array of sorted (timestamp, user_id) tuples.
    return plugin_instance.instance.fetch_incident_events(
        db_session=db_session,
        subject=incident,
        plugin_event_id=activity.plugin_event.id,
        oldest=oldest,
    )


def calculate_incident_response_cost_with_cost_model(
    incident: Incident, db_session: SessionLocal
) -> int:
    """Calculates the cost of an incident using the incident's cost model.

    This function aggregates all new incident costs based on plugin activity since the last incident cost update.
    If this is the first time performing cost calculation for this incident, it computes the total costs from the incident's creation.

    Args:
        incident: The incident to calculate the incident response cost for.
        db_session: The database session.

    Returns:
        int: The incident response cost in dollars.
    """

    participants_total_response_time_seconds = 0
    oldest = incident.created_at.replace(tzinfo=timezone.utc).timestamp()

    # Used for determining whether we've previously calculated the incident cost.
    current_time = datetime.now(tz=timezone.utc).replace(tzinfo=None)

    incident_response_cost = get_or_create_default_incident_response_cost(
        incident=incident, db_session=db_session
    )
    if not incident_response_cost:
        log.warning(f"Cannot calculate incident response cost for incident {incident.name}.")
        return 0

    # Ignore events that happened before the last incident cost update.
    if incident_response_cost.updated_at < current_time:
        oldest = incident_response_cost.updated_at.replace(tzinfo=timezone.utc).timestamp()

    # Get the cost model. Iterate through all the listed activities we want to record.
    for activity in incident.incident_type.cost_model.activities:

        # Array of sorted (timestamp, user_id) tuples.
        incident_events = fetch_incident_events(
            incident=incident, activity=activity, oldest=oldest, db_session=db_session
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

    hourly_rate = get_hourly_rate(incident.project)
    amount = calculate_response_cost(
        hourly_rate=hourly_rate,
        total_response_time_seconds=participants_total_response_time_seconds,
    )

    return incident.total_cost + amount


def get_participant_role_time_seconds(
    incident: Incident, participant_role: ParticipantRole, start_at: datetime
) -> int:
    """Calculates the time spent by a participant in an incident role starting from a given time.

    The participant's time spent in the incident role is adjusted based on the role's engagement multiplier.

    Args:
        incident: The incident the participant is part of.
        participant_role: The role of the participant and the time they assumed and renounced the role.
        start_at: Only time spent after this will be considered.

    Returns:
        int: The time spent by the participant in the incident role in seconds.
    """
    if participant_role.renounced_at and participant_role.renounced_at < start_at:
        # skip calculating already-recorded activity
        return 0

    if participant_role.role == ParticipantRoleType.observer:
        # skip calculating cost for participants with the observer role
        return 0

    if participant_role.activity == 0:
        # skip calculating cost for roles that have no activity
        return 0

    participant_role_assumed_at = participant_role.assumed_at

    # we set the renounced_at default time to the current time
    participant_role_renounced_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)

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

    # the time the participant has spent in the incident role since the last incident cost update
    participant_role_time = participant_role_renounced_at - max(
        participant_role_assumed_at, start_at
    )
    if participant_role_time.total_seconds() < 0:
        # the participant was added after the incident was marked as stable
        return 0

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
    return (
        participant_role_time_hours
        * SECONDS_IN_HOUR
        * get_engagement_multiplier(participant_role.role)
    )


def get_total_participant_roles_time_seconds(incident: Incident, start_at: datetime) -> int:
    """Calculates the time spent by all participants in this incident starting from a given time.

    The participant hours are adjusted based on their role(s)'s engagement multiplier.

    Args:
        incident: The incident the participant is part of.
        participant_role: The role of the participant and the time they assumed and renounced the role.
        start_at: Only time spent after this will be considered.

    Returns:
        int: The total time spent by all participants in the incident roles in seconds.

    """
    total_participants_roles_time_seconds = 0
    for participant in incident.participants:
        for participant_role in participant.participant_roles:
            total_participants_roles_time_seconds += get_participant_role_time_seconds(
                incident=incident,
                participant_role=participant_role,
                start_at=start_at,
            )
    return total_participants_roles_time_seconds


def calculate_incident_response_cost_with_classic_model(
    incident: Incident, db_session: SessionLocal, incident_review: bool = False
) -> int:
    """Calculates the cost of an incident using the classic incident cost model.

    This function aggregates all new incident costs since the last incident cost update. If this is the first time performing cost calculation for this incident, it computes the total costs from the incident's creation.

    Args:
        incident: The incident to calculate the incident response cost for.
        db_session: The database session.
        incident_review: Whether to add the incident review costs in this calculation.

    Returns:
        int: The incident response cost in dollars.
    """
    last_update = incident.created_at
    incident_review_hours = 0

    # Used for determining whether we've previously calculated the incident cost.
    curent_time = datetime.now(tz=timezone.utc).replace(tzinfo=None)

    incident_response_cost = get_or_create_default_incident_response_cost(
        incident=incident, db_session=db_session
    )
    if not incident_response_cost:
        return 0

    # Ignore activities that happened before the last incident cost update.
    if incident_response_cost.updated_at < curent_time:
        last_update = incident_response_cost.updated_at

    # TODO: Implement a more robust way to ensure we are calculating the incident review hours only once.
    if incident_review:
        incident_review_hours = get_incident_review_hours(incident)

    # Aggregates the incident response costs accumulated since the last incident cost update
    total_participants_roles_time_seconds = get_total_participant_roles_time_seconds(
        incident, start_at=last_update
    )

    # Calculates and rounds up the incident cost
    hourly_rate = get_hourly_rate(incident.project)
    amount = calculate_response_cost(
        hourly_rate=hourly_rate,
        total_response_time_seconds=total_participants_roles_time_seconds,
        incident_review_hours=incident_review_hours,
    )

    return incident_response_cost.amount + amount


def calculate_incident_response_cost(
    incident_id: int, db_session: SessionLocal, incident_review: bool = False
) -> int:
    """Calculates the response cost of a given incident."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    if not incident:
        log.warning(f"Incident with id {incident_id} not found.")
        return 0

    incident_type = incident.incident_type
    if not incident_type:
        log.warning(f"Incident type for incident {incident.name} not found.")
        return 0

    if incident_type.cost_model and incident_type.cost_model.enabled:
        log.debug(
            f"Calculating {incident.name} incident cost with model {incident_type.cost_model}."
        )
        return calculate_incident_response_cost_with_cost_model(
            incident=incident, db_session=db_session
        )
    else:
        log.debug("No incident cost model found. Defaulting to classic incident cost model.")

        return calculate_incident_response_cost_with_classic_model(
            incident=incident, db_session=db_session, incident_review=incident_review
        )


def update_incident_response_cost(
    incident_id: int, db_session: SessionLocal, incident_review: bool = False
) -> int:
    """Updates the response cost of a given incident.

    Args:
        incident_id: The incident id.
        db_session: The database session.
        incident_review: Whether to add the incident review costs in this calculation.

    Returns:
        int: The incident response cost in dollars.
    """
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    amount = calculate_incident_response_cost(
        incident_id=incident.id, db_session=db_session, incident_review=incident_review
    )

    incident_response_cost = get_default_incident_response_cost(
        incident=incident, db_session=db_session
    )

    if not incident_response_cost:
        log.warning(f"Cannot calculate incident response cost for incident {incident.name}.")
        return 0

    # we update the cost amount only if the incident cost has changed
    if incident_response_cost.amount != amount:
        incident_response_cost.amount = amount
        incident.incident_costs.append(incident_response_cost)
        db_session.add(incident)
        db_session.commit()

    return incident_response_cost.amount
