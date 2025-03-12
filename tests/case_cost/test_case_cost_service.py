def test_get(session, case_cost):
    from dispatch.case_cost.service import get

    t_case_cost = get(db_session=session, case_cost_id=case_cost.id)
    assert t_case_cost.id == case_cost.id


def test_get_by_case_id(session, case_cost):
    from dispatch.case_cost.service import get_by_case_id

    assert get_by_case_id(db_session=session, case_id=case_cost.case_id)


def test_get_all(session, case_costs):
    from dispatch.case_cost.service import get_all

    t_case_costs = get_all(db_session=session).all()
    assert t_case_costs


def test_create(session, case_cost_type, project):
    from dispatch.case_cost.service import create
    from dispatch.case_cost.models import CaseCostCreate

    amount = 10000

    case_cost_in = CaseCostCreate(
        amount=amount,
        case_cost_type=case_cost_type,
        project=project,
    )
    case_cost = create(db_session=session, case_cost_in=case_cost_in)
    assert case_cost


def test_get_or_create__create(session, case_cost_type, project):
    from dispatch.case_cost.service import get_or_create
    from dispatch.case_cost.models import CaseCostCreate

    amount = 10000

    case_cost_in = CaseCostCreate(
        amount=amount,
        case_cost_type=case_cost_type,
        project=project,
    )
    case_cost = get_or_create(db_session=session, case_cost_in=case_cost_in)
    assert case_cost


def test_update(session, case_cost, case_cost_type):
    from dispatch.case_cost.service import update
    from dispatch.case_cost.models import CaseCostUpdate

    amount = 10001

    case_cost_in = CaseCostUpdate(amount=amount, case_cost_type=case_cost_type)
    case_cost = update(db_session=session, case_cost=case_cost, case_cost_in=case_cost_in)
    assert case_cost.amount == amount


def test_delete(session, case_cost):
    from dispatch.case_cost.service import delete, get

    delete(db_session=session, case_cost_id=case_cost.id)
    assert not get(db_session=session, case_cost_id=case_cost.id)


def test_fetch_case_event__enabled_plugins(
    case,
    cost_model_activity,
    session,
    conversation_plugin_instance,
):
    from dispatch.case_cost.service import fetch_case_events

    conversation_plugin_instance.project_id = case.project.id
    cost_model_activity.plugin_event.plugin = conversation_plugin_instance.plugin
    conversation_plugin_instance.enabled = True

    assert fetch_case_events(case, cost_model_activity, oldest="0", db_session=session)


def test_fetch_case_event__no_enabled_plugins(
    case,
    cost_model_activity,
    session,
    conversation_plugin_instance,
):
    from dispatch.case_cost.service import fetch_case_events

    conversation_plugin_instance.project_id = case.project.id
    cost_model_activity.plugin_event.plugin = conversation_plugin_instance.plugin
    conversation_plugin_instance.enabled = False

    assert not fetch_case_events(case, cost_model_activity, oldest="0", db_session=session)


def test_update_case_participant_activities__create(
    case,
    session,
    conversation_plugin_instance,
    cost_model_activity,
    participant,
    case_cost_type,
    conversation,
):
    """Tests that case participant activity is created the first time a case updates its response cost."""
    from dispatch.case_cost.service import update_case_participant_activities
    from dispatch.case_cost_type import service as case_cost_type_service

    # Set up incoming plugin events.
    conversation_plugin_instance.project_id = case.project.id
    cost_model_activity.plugin_event.plugin = conversation_plugin_instance.plugin
    participant.user_conversation_id = "0XDECAFBAD"
    participant.case = case

    # Set up a default case cost type.
    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    case_cost_type.default = True
    case_cost_type.project = case.project

    # Set up case.
    case.case_type.cost_model.enabled = True
    case.case_type.cost_model.activities = [cost_model_activity]

    # Set up case conversation.
    case.conversation = conversation
    case.dedicated_channel = True

    # Assert that the case participant activity is created.
    assert update_case_participant_activities(case=case, db_session=session)


def test_update_case_participant_activities__no_cost_model(case, session):
    """Tests that the case participant activity is not created if the cost model is not enabled."""
    from dispatch.case_cost.service import update_case_participant_activities
    from dispatch.participant_activity.service import (
        get_all_case_participant_activities_for_case,
    )

    case.cost_model = None
    assert not update_case_participant_activities(case=case, db_session=session)

    activities = get_all_case_participant_activities_for_case(db_session=session, case_id=case.id)
    assert not activities


def test_update_case_participant_activities__no_enabled_plugins(
    case,
    session,
    cost_model_activity,
    participant,
    case_cost_type,
    conversation,
    plugin_instance,
):
    """Tests that the case participant activity is not created if plugins are not enabled."""
    from dispatch.case.service import get
    from dispatch.case_cost.service import update_case_participant_activities
    from dispatch.case_cost_type import service as case_cost_type_service
    from dispatch.participant_activity.service import (
        get_all_case_participant_activities_for_case,
    )

    # Set up. Disable the plugin instance for the cost model plugin event.
    plugin_instance.project_id = case.project.id
    plugin_instance.enabled = False
    cost_model_activity.plugin_event.plugin = plugin_instance.plugin
    participant.user_conversation_id = "0XDECAFBAD"
    participant.case = case

    # Set up a default case cost type.
    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    case_cost_type.default = True
    case_cost_type.project = case.project

    # Set up case.
    case = get(db_session=session, case_id=case.id)
    case.case_type.cost_model.enabled = True
    case.case_type.cost_model.activities = [cost_model_activity]
    case.conversation = conversation

    # Assert that no participant activity was created.
    assert not update_case_participant_activities(case=case, db_session=session)

    activities = get_all_case_participant_activities_for_case(db_session=session, case_id=case.id)
    assert not activities


def test_get_engagement_multiplier():
    """Tests that engagement multipliers are returned correctly for different roles."""
    from dispatch.participant_role.models import ParticipantRoleType
    from dispatch.case_cost.service import get_engagement_multiplier

    assert get_engagement_multiplier(ParticipantRoleType.assignee) == 1
    assert get_engagement_multiplier(ParticipantRoleType.reporter) == 0.5
    assert get_engagement_multiplier(ParticipantRoleType.participant) == 0.5
    assert get_engagement_multiplier(ParticipantRoleType.observer) == 0


def test_calculate_case_response_cost(case, session, participant_activity, case_cost_type):
    """Tests that the case response cost is calculated correctly for both models."""
    from dispatch.case_cost.service import (
        calculate_case_response_cost,
        calculate_response_cost,
        get_hourly_rate,
    )
    from dispatch.case.enums import CostModelType

    # Set up participant activity
    participant_activity.case = case

    # Set up cost types for both models
    case_cost_type.model_type = CostModelType.new
    case_cost_type.project = case.project

    # Calculate costs using both models
    costs = calculate_case_response_cost(case=case, db_session=session)

    # Assert both models returned costs
    assert CostModelType.new in costs
    assert CostModelType.classic in costs

    # Verify new model cost calculation
    expected_cost = calculate_response_cost(
        hourly_rate=get_hourly_rate(case.project),
        total_response_time_seconds=(
            participant_activity.ended_at - participant_activity.started_at
        ).total_seconds(),
    )
    assert costs[CostModelType.new] == expected_cost


def test_calculate_case_response_cost_classic(
    case, session, participant, participant_role, case_cost_type
):
    """Tests that the classic cost model calculates costs correctly."""
    from datetime import datetime, timedelta, timezone
    import math
    from dispatch.case_cost.service import (
        calculate_case_response_cost_classic,
        get_hourly_rate,
    )
    from dispatch.participant_role.models import ParticipantRoleType
    from dispatch.case.enums import CostModelType

    # Set up timestamps with exact timing
    now = datetime.now(timezone.utc).replace(microsecond=0)
    one_hour_ago = (now - timedelta(hours=1)).replace(microsecond=0)
    case.created_at = one_hour_ago.replace(tzinfo=None)

    # Set up participant role with exact timing
    participant_role.role = ParticipantRoleType.assignee  # Full engagement multiplier
    participant_role.assumed_at = one_hour_ago.replace(tzinfo=None)
    participant_role.renounced_at = now.replace(tzinfo=None)  # Set exact end time

    # Set up participant
    participant.participant_roles = [participant_role]
    case.participants.append(participant)

    # Set up cost type for classic model
    case_cost_type.model_type = CostModelType.classic
    case_cost_type.project = case.project

    # Calculate cost
    cost = calculate_case_response_cost_classic(case=case, db_session=session)

    # Verify cost calculation
    hourly_rate = get_hourly_rate(case.project)
    expected_cost = math.ceil(hourly_rate)  # Cost for 1 hour with full engagement
    assert cost > 0
    assert cost == expected_cost  # Should be exactly the hourly rate for 1 hour at full engagement


def test_get_participant_role_time_seconds(case, participant_role):
    """Tests that participant role time is calculated correctly."""
    from datetime import datetime, timedelta, timezone
    from dispatch.case_cost.service import get_participant_role_time_seconds
    from dispatch.participant_role.models import ParticipantRoleType

    # Set up test times with exact 1 hour difference
    now = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)
    one_hour_ago = (now - timedelta(hours=1)).replace(microsecond=0)

    # Set up participant role for full engagement test with exact timing
    participant_role.role = ParticipantRoleType.assignee
    participant_role.assumed_at = one_hour_ago
    participant_role.renounced_at = now  # Set exact end time instead of None

    # Test full engagement role (assignee)
    time_seconds = get_participant_role_time_seconds(case=case, participant_role=participant_role)
    assert time_seconds > 0
    assert time_seconds <= 3600  # Should not exceed 1 hour

    # Set up participant role for no engagement test
    participant_role.role = ParticipantRoleType.observer

    # Test no engagement role (observer)
    time_seconds = get_participant_role_time_seconds(case=case, participant_role=participant_role)
    assert time_seconds == 0


def test_get_total_participant_roles_time_seconds(case, participant, participant_role):
    """Tests that total participant role time is calculated correctly."""
    from datetime import datetime, timedelta, timezone
    from dispatch.case_cost.service import get_total_participant_roles_time_seconds
    from dispatch.participant_role.models import ParticipantRoleType

    # Set up test times with exact 1 hour difference
    now = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)
    one_hour_ago = (now - timedelta(hours=1)).replace(microsecond=0)

    # Set up participant role with exact timing
    participant_role.role = ParticipantRoleType.assignee
    participant_role.assumed_at = one_hour_ago
    participant_role.renounced_at = now  # Set exact end time instead of None

    # Add role to participant and participant to case
    participant.participant_roles = [participant_role]
    case.participants.append(participant)

    # Calculate total time
    total_time = get_total_participant_roles_time_seconds(case=case)

    assert total_time > 0
    assert total_time <= 3600  # Should not exceed 1 hour


def test_update_case_response_cost(
    case, session, participant_activity, case_cost_type, cost_model_activity
):
    """Tests that the case response cost is created correctly."""
    from dispatch.case.enums import CostModelType
    from dispatch.case_cost.service import update_case_response_cost

    # Set up participant activity
    participant_activity.case = case

    # Set up cost types for both models
    case_cost_type.model_type = CostModelType.new
    case_cost_type.project = case.project

    # Set up case type cost model
    case.case_type.cost_model.enabled = True
    case.case_type.cost_model.activities = [cost_model_activity]

    # Assert that costs were calculated
    results = update_case_response_cost(case=case, db_session=session)
    assert results[CostModelType.new] > 0
    assert results[CostModelType.classic] >= 0
