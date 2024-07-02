from datetime import datetime, timedelta, timezone
import logging
import math
from typing import List, Optional

from dispatch.database.core import SessionLocal
from dispatch.cost_model.models import CostModelActivity
from dispatch.case import service as case_service
from dispatch.case.enums import CaseStatus
from dispatch.case.models import Case
from dispatch.case.type.models import CaseType
from dispatch.case_cost_type import service as case_cost_type_service
from dispatch.case_cost_type.models import CaseCostTypeRead
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantRead
from dispatch.participant_activity import service as participant_activity_service
from dispatch.participant_activity.models import ParticipantActivityCreate
from dispatch.participant_role.models import ParticipantRoleType, ParticipantRole
from dispatch.plugin import service as plugin_service

from .models import CaseCost, CaseCostCreate, CaseCostUpdate


HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600
log = logging.getLogger(__name__)


def get(*, db_session, case_cost_id: int) -> Optional[CaseCost]:
    """Gets an case cost by its id."""
    return db_session.query(CaseCost).filter(CaseCost.id == case_cost_id).one_or_none()


def get_by_case_id(*, db_session, case_id: int) -> List[Optional[CaseCost]]:
    """Gets case costs by their case id."""
    return db_session.query(CaseCost).filter(CaseCost.case_id == case_id).all()


def get_by_case_id_and_case_cost_type_id(
    *, db_session, case_id: int, case_cost_type_id: int
) -> Optional[CaseCost]:
    """Gets case costs by their case id and case cost type id."""
    return (
        db_session.query(CaseCost)
        .filter(CaseCost.case_id == case_id)
        .filter(CaseCost.case_cost_type_id == case_cost_type_id)
        .one_or_none()
    )


def get_all(*, db_session) -> List[Optional[CaseCost]]:
    """Gets all case costs."""
    return db_session.query(CaseCost)


def get_or_create(*, db_session, case_cost_in: CaseCostCreate | CaseCostUpdate) -> CaseCost:
    """Gets or creates an case cost object."""
    if type(case_cost_in) is CaseCostUpdate and case_cost_in.id:
        case_cost = get(db_session=db_session, case_cost_id=case_cost_in.id)
    else:
        case_cost = create(db_session=db_session, case_cost_in=case_cost_in)

    return case_cost


def create(*, db_session, case_cost_in: CaseCostCreate) -> CaseCost:
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


def update(*, db_session, case_cost: CaseCost, case_cost_in: CaseCostUpdate) -> CaseCost:
    """Updates an case cost."""
    case_cost_data = case_cost.dict()
    update_data = case_cost_in.dict(skip_defaults=True)

    for field in case_cost_data:
        if field in update_data:
            setattr(case_cost, field, update_data[field])

    db_session.commit()
    return case_cost


def delete(*, db_session, case_cost_id: int):
    """Deletes an existing case cost."""
    db_session.query(CaseCost).filter(CaseCost.id == case_cost_id).delete()
    db_session.commit()


def get_hourly_rate(project) -> int:
    """Calculates and rounds up the employee hourly rate within a project."""
    return math.ceil(project.annual_employee_cost / project.business_year_hours)


def update_case_response_cost_for_case_type(db_session, case_type: CaseType) -> None:
    """Calculate the response cost of all non-closed cases associated with this case type."""
    cases = case_service.get_all_open_by_case_type(db_session=db_session, case_type_id=case_type.id)
    for case in cases:
        update_case_response_cost(case_id=case.id, db_session=db_session)


def calculate_response_cost(hourly_rate, total_response_time_seconds) -> int:
    """Calculates and rounds up the case response cost."""
    return math.ceil(((total_response_time_seconds / SECONDS_IN_HOUR)) * hourly_rate)


def get_default_case_response_cost(case: Case, db_session: SessionLocal) -> Optional[CaseCost]:
    response_cost_type = case_cost_type_service.get_default(
        db_session=db_session, project_id=case.project.id
    )

    if not response_cost_type:
        log.warning(
            f"A default cost type for response cost doesn't exist in the {case.project.name} project and organization {case.project.organization.name}. Response costs for case {case.name} won't be calculated."
        )
        return None

    return get_by_case_id_and_case_cost_type_id(
        db_session=db_session,
        case_id=case.id,
        case_cost_type_id=response_cost_type.id,
    )


def get_or_create_default_case_response_cost(
    case: Case, db_session: SessionLocal
) -> Optional[CaseCost]:
    """Gets or creates the default case cost for an case.

    The default case cost is the cost associated with the participant effort in an case's response.
    """
    response_cost_type = case_cost_type_service.get_default(
        db_session=db_session, project_id=case.project.id
    )

    if not response_cost_type:
        log.warning(
            f"A default cost type for response cost doesn't exist in the {case.project.name} project and organization {case.project.organization.name}. Response costs for case {case.name} won't be calculated."
        )
        return None

    case_response_cost = get_by_case_id_and_case_cost_type_id(
        db_session=db_session,
        case_id=case.id,
        case_cost_type_id=response_cost_type.id,
    )

    if not case_response_cost:
        # we create the response cost if it doesn't exist
        case_cost_type = CaseCostTypeRead.from_orm(response_cost_type)
        case_cost_in = CaseCostCreate(case_cost_type=case_cost_type, project=case.project)
        case_response_cost = create(db_session=db_session, case_cost_in=case_cost_in)
        case.case_costs.append(case_response_cost)
        db_session.add(case)
        db_session.commit()

    return case_response_cost


def fetch_case_events(
    case: Case, activity: CostModelActivity, oldest: str, db_session: SessionLocal
) -> List[Optional[tuple[datetime.timestamp, str]]]:
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

    # Array of sorted (timestamp, user_id) tuples.
    return plugin_instance.instance.fetch_events(
        db_session=db_session,
        subject=case,
        plugin_event_id=activity.plugin_event.id,
        oldest=oldest,
    )


def calculate_case_response_cost_with_cost_model(case: Case, db_session: SessionLocal) -> int:
    """Calculates the cost of an case using the case's cost model.

    This function aggregates all new case costs based on plugin activity since the last case cost update.
    If this is the first time performing cost calculation for this case, it computes the total costs from the case's creation.

    Args:
        case: The case to calculate the case response cost for.
        db_session: The database session.

    Returns:
        int: The case response cost in dollars.
    """

    participants_total_response_time_seconds = 0
    oldest = case.created_at.replace(tzinfo=timezone.utc).timestamp()

    # Used for determining whether we've previously calculated the case cost.
    current_time = datetime.now(tz=timezone.utc).replace(tzinfo=None)

    case_response_cost = get_or_create_default_case_response_cost(case=case, db_session=db_session)
    if not case_response_cost:
        log.warning(f"Cannot calculate case response cost for case {case.name}.")
        return 0

    # Ignore events that happened before the last case cost update.
    if case_response_cost.updated_at < current_time:
        oldest = case_response_cost.updated_at.replace(tzinfo=timezone.utc).timestamp()

    if case.case_type.cost_model:
        # Get the cost model. Iterate through all the listed activities we want to record.
        for activity in case.case_type.cost_model.activities:

            # Array of sorted (timestamp, user_id) tuples.
            case_events = fetch_case_events(
                case=case, activity=activity, oldest=oldest, db_session=db_session
            )

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

                if participant_response_time := participant_activity_service.create_or_update(
                    db_session=db_session, activity_in=activity_in
                ):
                    participants_total_response_time_seconds += (
                        participant_response_time.total_seconds()
                    )

    hourly_rate = get_hourly_rate(case.project)
    amount = calculate_response_cost(
        hourly_rate=hourly_rate,
        total_response_time_seconds=participants_total_response_time_seconds,
    )

    return case.total_cost + amount


def get_participant_role_time_seconds(
    case: Case, participant_role: ParticipantRole, start_at: datetime
) -> int:
    """Calculates the time spent by a participant in an case role starting from a given time.

    Args:
        case: The case the participant is part of.
        participant_role: The role of the participant and the time they assumed and renounced the role.
        start_at: Only time spent after this will be considered.

    Returns:
        int: The time spent by the participant in the case role in seconds.
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

    if case.status in [CaseStatus.new, CaseStatus.triage]:
        if participant_role.renounced_at:
            # the participant left the conversation or got assigned another role
            # we use the role's renounced_at time
            participant_role_renounced_at = participant_role.renounced_at
    else:
        # we set the renounced_at default time to when the case was marked as escalated or closed
        if case.escalated_at:
            participant_role_renounced_at = case.escalated_at

        if case.closed_at:
            participant_role_renounced_at = case.closed_at

        if participant_role.renounced_at:
            # the participant left the conversation or got assigned another role
            if participant_role.renounced_at < participant_role_renounced_at:
                # we use the role's renounced_at time if it happened before the
                # case was marked as stable or closed
                participant_role_renounced_at = participant_role.renounced_at

    # the time the participant has spent in the case role since the last case cost update
    participant_role_time = participant_role_renounced_at - max(
        participant_role_assumed_at, start_at
    )
    if participant_role_time.total_seconds() < 0:
        # the participant was added after the case was marked as stable
        return 0

    # we calculate the number of hours the participant has spent in the case role
    participant_role_time_hours = participant_role_time.total_seconds() / SECONDS_IN_HOUR

    # we make the assumption that participants only spend 8 hours a day working on the case,
    # if the case goes past 24hrs
    # TODO(mvilanova): adjust based on case priority
    if participant_role_time_hours > HOURS_IN_DAY:
        days, hours = divmod(participant_role_time_hours, HOURS_IN_DAY)
        participant_role_time_hours = math.ceil(((days * HOURS_IN_DAY) / 3) + hours)

    # we make the assumption that participants spend more or less time based on their role
    # and we adjust the time spent based on that
    return participant_role_time_hours * SECONDS_IN_HOUR


def get_total_participant_roles_time_seconds(case: Case, start_at: datetime) -> int:
    """Calculates the time spent by all participants in this case starting from a given time.

    Args:
        case: The case the participant is part of.
        participant_role: The role of the participant and the time they assumed and renounced the role.
        start_at: Only time spent after this will be considered.

    Returns:
        int: The total time spent by all participants in the case roles in seconds.

    """
    total_participants_roles_time_seconds = 0
    for participant in case.participants:
        for participant_role in participant.participant_roles:
            total_participants_roles_time_seconds += get_participant_role_time_seconds(
                case=case,
                participant_role=participant_role,
                start_at=start_at,
            )
    return total_participants_roles_time_seconds


def calculate_case_response_cost(case_id: int, db_session: SessionLocal) -> int:
    """Calculates the response cost of a given case.

    If there is no cost model, the case cost will not be calculated.
    """
    case = case_service.get(db_session=db_session, case_id=case_id)
    if not case:
        log.warning(f"Case with id {case_id} not found.")
        return 0

    case_type = case.case_type
    if not case_type:
        print(f"Case type for case {case.name} not found.")
        return case.total_cost

    if not case_type.cost_model:
        log.debug("No case cost model found. Skipping this case.")
        return case.total_cost

    if not case_type.cost_model.enabled:
        log.debug("Case cost model is not enabled. Skipping this case.")
        return case.total_cost

    log.debug(f"Calculating {case.name} case cost with model {case_type.cost_model}.")
    return calculate_case_response_cost_with_cost_model(case=case, db_session=db_session)


def update_case_response_cost(case_id: int, db_session: SessionLocal) -> int:
    """Updates the response cost of a given case.

    Args:
        case_id: The case id.
        db_session: The database session.

    Returns:
        int: The case response cost in dollars.
    """
    case = case_service.get(db_session=db_session, case_id=case_id)

    amount = calculate_case_response_cost(case_id=case.id, db_session=db_session)

    case_response_cost = get_default_case_response_cost(case=case, db_session=db_session)

    if not case_response_cost:
        log.warning(f"Cannot calculate case response cost for case {case.name}.")
        return 0

    # we update the cost amount only if the case cost has changed
    if case_response_cost.amount != amount:
        case_response_cost.amount = amount
        case.case_costs.append(case_response_cost)
        db_session.add(case)
        db_session.commit()

    return case_response_cost.amount
