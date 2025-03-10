from datetime import datetime, timedelta, timezone
import logging
import math
from typing import Optional

from sqlalchemy.orm import Session

from dispatch.cost_model.models import CostModelActivity
from dispatch.case import service as case_service
from dispatch.case.models import Case
from dispatch.case.type.models import CaseType
from dispatch.case_cost_type import service as case_cost_type_service
from dispatch.case.enums import CostModelType
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantRead
from dispatch.participant_activity import service as participant_activity_service
from dispatch.participant_activity.models import ParticipantActivityCreate, ParticipantActivity
from dispatch.plugin import service as plugin_service

from .models import CaseCost, CaseCostCreate, CaseCostUpdate


HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600
log = logging.getLogger(__name__)


def get(*, db_session: Session, case_cost_id: int) -> Optional[CaseCost]:
    """Gets a case cost by its id."""
    return db_session.query(CaseCost).filter(CaseCost.id == case_cost_id).one_or_none()


def get_by_case_id(*, db_session, case_id: int) -> list[Optional[CaseCost]]:
    """Gets case costs by their case id."""
    return db_session.query(CaseCost).filter(CaseCost.case_id == case_id).all()


def get_by_case_id_and_case_cost_type_id(
    *, db_session: Session, case_id: int, case_cost_type_id: int
) -> Optional[CaseCost]:
    """Gets case costs by their case id and case cost type id."""
    return (
        db_session.query(CaseCost)
        .filter(CaseCost.case_id == case_id)
        .filter(CaseCost.case_cost_type_id == case_cost_type_id)
        .order_by(CaseCost.id.asc())
        .first()
    )


def get_all(*, db_session: Session) -> list[Optional[CaseCost]]:
    """Gets all case costs."""
    return db_session.query(CaseCost)


def get_or_create(
    *, db_session: Session, case_cost_in: CaseCostCreate | CaseCostUpdate
) -> CaseCost:
    """Gets or creates a case cost object."""
    if type(case_cost_in) is CaseCostUpdate and case_cost_in.id:
        case_cost = get(db_session=db_session, case_cost_id=case_cost_in.id)
    else:
        case_cost = create(db_session=db_session, case_cost_in=case_cost_in)

    return case_cost


def create(*, db_session: Session, case_cost_in: CaseCostCreate) -> CaseCost:
    """Creates a new case cost."""
    case_cost_type = case_cost_type_service.get(
        db_session=db_session, case_cost_type_id=case_cost_in.case_cost_type.id
    )
    case_cost = CaseCost(
        **case_cost_in.dict(exclude={"case_cost_type", "project"}),
        case_cost_type=case_cost_type,
        project=case_cost_type.project,
    )
    db_session.add(case_cost)
    db_session.commit()

    return case_cost


def update(*, db_session: Session, case_cost: CaseCost, case_cost_in: CaseCostUpdate) -> CaseCost:
    """Updates a case cost."""
    case_cost_data = case_cost.dict()
    update_data = case_cost_in.dict(skip_defaults=True)

    for field in case_cost_data:
        if field in update_data:
            setattr(case_cost, field, update_data[field])

    db_session.commit()
    return case_cost


def delete(*, db_session: Session, case_cost_id: int):
    """Deletes an existing case cost."""
    db_session.query(CaseCost).filter(CaseCost.id == case_cost_id).delete()
    db_session.commit()


def get_hourly_rate(project) -> int:
    """Calculates and rounds up the employee hourly rate within a project."""
    return math.ceil(project.annual_employee_cost / project.business_year_hours)


def update_case_response_cost_for_case_type(db_session: Session, case_type: CaseType) -> None:
    """Calculate the response cost of all non-closed cases associated with this case type."""
    cases = case_service.get_all_open_by_case_type(db_session=db_session, case_type_id=case_type.id)
    for case in cases:
        update_case_response_cost(case=case, db_session=db_session)


def calculate_response_cost(hourly_rate, total_response_time_seconds) -> int:
    """Calculates and rounds up the case response cost."""
    return math.ceil((total_response_time_seconds / SECONDS_IN_HOUR) * hourly_rate)


def get_or_create_case_response_cost_by_model_type(
    case: Case, model_type: str, db_session: Session
) -> Optional[CaseCost]:
    """Gets a case response cost for a specific model type."""
    # Find the cost type matching the requested model type for the project
    response_cost_type = case_cost_type_service.get_or_create_response_cost_type(
        db_session=db_session, project_id=case.project.id, model_type=model_type
    )

    if not response_cost_type:
        log.warning(
            f"A default cost type for model type {model_type} doesn't exist and could not be created in the {case.project.name} project. "
            f"Response costs for case {case.name} won't be calculated for this model."
        )
        return None

    # Retrieve or create the case cost for the given case and cost type
    case_cost = get_by_case_id_and_case_cost_type_id(
        db_session=db_session, case_id=case.id, case_cost_type_id=response_cost_type.id
    )
    if not case_cost:
        case_cost = CaseCostCreate(
            case=case, case_cost_type=response_cost_type, amount=0, project=case.project
        )
        case_cost = create(db_session=db_session, case_cost_in=case_cost)

    return case_cost


def fetch_case_events(
    case: Case, activity: CostModelActivity, oldest: str, db_session: Session
) -> list[Optional[tuple[datetime.timestamp, str]]]:
    """Fetches case events for a given case and cost model activity.

    Args:
        case: The case to fetch events for.
        activity: The activity to fetch events for. This defines the plugin event to fetch and how much response effort each event requires.
        oldest: The timestamp to start fetching events from.
        db_session: The database session.

    Returns:
        list[Optional[tuple[datetime.timestamp, str]]]: A list of tuples containing the timestamp and user_id of each event.
    """

    plugin_instance = plugin_service.get_active_instance_by_slug(
        db_session=db_session,
        slug=activity.plugin_event.plugin.slug,
        project_id=case.project.id,
    )
    if not plugin_instance:
        log.warning(
            f"Cannot fetch cost model activity. Its associated plugin {activity.plugin_event.plugin.title} is not enabled."
        )
        return []

    return plugin_instance.instance.fetch_events(
        db_session=db_session,
        subject=case,
        plugin_event_id=activity.plugin_event.id,
        oldest=oldest,
    )


def update_case_participant_activities(
    case: Case, db_session: Session
) -> ParticipantActivity | None:
    """Records or updates case participant activities using the case's cost model.

    This function records and/or updates all new case participant activities since the last case cost update.

    Args:
        case: The case to calculate the case response cost for.
        db_session: The database session.

    Returns:
        ParticipantActivity | None: The most recent participant activity created or updated.
    """
    if not case:
        log.warning(f"Case with id {case.id} not found.")
        return

    case_type = case.case_type
    if not case_type:
        log.debug(f"Case type for case {case.name} not found.")
        return

    if not case_type.cost_model:
        log.debug("No case cost model found. Skipping this case.")
        return

    if not case_type.cost_model.enabled:
        log.debug("Case cost model is not enabled. Skipping this case.")
        return

    log.debug(f"Calculating {case.name} case cost with model {case_type.cost_model}.")
    oldest = case.created_at.replace(tzinfo=timezone.utc).timestamp()

    # Used for determining whether we've previously calculated the case cost.
    current_time = datetime.now(tz=timezone.utc).replace(tzinfo=None)

    case_response_cost = get_or_create_case_response_cost_by_model_type(
        case=case, db_session=db_session, model_type=CostModelType.new
    )
    if not case_response_cost:
        log.warning(
            f"Cannot calculate case response cost for case {case.name}. No default case response cost type created or found."
        )
        return

    most_recent_activity = None
    # Ignore events that happened before the last case cost update.
    if case_response_cost.updated_at < current_time:
        oldest = case_response_cost.updated_at.replace(tzinfo=timezone.utc).timestamp()

    case_events = []
    # Get the cost model. Iterate through all the listed activities we want to record.
    if case.case_type.cost_model:
        for activity in case.case_type.cost_model.activities:
            # Array of sorted (timestamp, user_id) tuples.
            case_events.extend(
                fetch_case_events(
                    case=case, activity=activity, oldest=oldest, db_session=db_session
                )
            )

        # Sort case_events by timestamp
        sorted(case_events, key=lambda x: x[0])

        for ts, user_id in case_events:
            participant = participant_service.get_by_case_id_and_conversation_id(
                db_session=db_session,
                case_id=case.id,
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
                case=case,
            )

            most_recent_activity = participant_activity_service.create_or_update(
                db_session=db_session, activity_in=activity_in
            )
    return most_recent_activity


def calculate_case_response_cost(case: Case, db_session: Session) -> int:
    """Calculates the response cost of a given case."""
    # Iterate through all the listed activities and aggregate the total participant response time spent on the case.
    participants_total_response_time = timedelta(0)
    participant_activities = (
        participant_activity_service.get_all_case_participant_activities_for_case(
            db_session=db_session, case_id=case.id
        )
    )
    for participant_activity in participant_activities:
        participants_total_response_time += (
            participant_activity.ended_at - participant_activity.started_at
        )

    hourly_rate = get_hourly_rate(case.project)
    amount = calculate_response_cost(
        hourly_rate=hourly_rate,
        total_response_time_seconds=participants_total_response_time.total_seconds(),
    )
    return amount


def update_case_response_cost(case: Case, db_session: Session) -> int:
    """Updates the response cost of a given case.

    This function logs all case participant activities since the last case cost update and
    recalculates the case response cost using the new cost model.

    Args:
        case: The case to update costs for.
        db_session: The database session.

    Returns:
        dict[str, int]: Dictionary containing costs from both models {'new': new_cost, 'classic': classic_cost}
    """
    # Update case participant activities before calculating costs
    update_case_participant_activities(case=case, db_session=db_session)

    results = {}

    # Calculate and update new model cost
    new_amount = calculate_case_response_cost(case=case, db_session=db_session)
    new_cost = get_or_create_case_response_cost_by_model_type(
        case=case, model_type=CostModelType.new, db_session=db_session
    )

    if new_cost:
        if new_cost.amount != new_amount:
            new_cost.amount = new_amount
            case.case_costs.append(new_cost)
            db_session.add(case)
            db_session.commit()
        results[CostModelType.new] = new_cost.amount

    return results
