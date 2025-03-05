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


def test_calculate_case_response_cost(case, session, participant_activity):
    """Tests that the case response cost is calculated correctly."""
    from dispatch.case_cost.service import (
        calculate_case_response_cost,
        calculate_response_cost,
        get_hourly_rate,
    )

    # Set up participant activity.
    participant_activity.case = case

    # Assert that the response cost was calculated correctly.
    response_cost = calculate_case_response_cost(case=case, db_session=session)
    assert response_cost == calculate_response_cost(
        hourly_rate=get_hourly_rate(case.project),
        total_response_time_seconds=(
            participant_activity.ended_at - participant_activity.started_at
        ).total_seconds(),
    )


def test_update_case_response_cost(case, session, participant_activity, case_cost_type):
    """Tests that the case response cost is created correctly."""
    from dispatch.case.enums import CostModelType
    from dispatch.case_cost.service import update_case_response_cost
    from dispatch.case_cost_type import service as case_cost_type_service

    # Set up participant activity
    participant_activity.case = case

    # Set up default case cost type
    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.model_type = None
    case_cost_type.project = case.project
    case_cost_type.model_type = CostModelType.new

    # Assert that costs were calculated
    results = update_case_response_cost(case=case, db_session=session)
    assert results[CostModelType.new] > 0


def test_update_case_response_cost__fail_no_cost_types(case, session):
    """Tests that the case response cost calculation handles missing cost types."""
    from dispatch.case.enums import CostModelType
    from dispatch.case_cost.service import (
        update_case_response_cost,
        get_by_case_id,
    )
    from dispatch.case_cost_type import service as case_cost_type_service

    # Ensure there are no default cost types for any model
    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.model_type = None

    # Calculate costs
    results = update_case_response_cost(case=case, db_session=session)

    # Verify no costs were calculated
    assert isinstance(results, dict)
    assert not results[CostModelType.new]
    assert not get_by_case_id(db_session=session, case_id=case.id)
