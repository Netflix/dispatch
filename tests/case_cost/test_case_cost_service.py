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


def test_calculate_case_response_cost(
    session,
    case,
    case_cost_type,
    cost_model_activity,
    conversation_plugin_instance,
    conversation,
    participant,
):
    """Tests that the case cost is calculated correctly when a cost model is enabled."""
    from datetime import timedelta
    import math
    from dispatch.case_cost.service import update_case_response_cost, get_hourly_rate
    from dispatch.case_cost_type import service as case_cost_type_service
    from dispatch.participant_activity.service import (
        get_all_case_participant_activities_for_case,
    )

    SECONDS_IN_HOUR = 3600
    orig_total_case_cost = case.total_cost

    # Set incoming plugin events.
    conversation_plugin_instance.project_id = case.project.id
    cost_model_activity.plugin_event.plugin = conversation_plugin_instance.plugin
    participant.user_conversation_id = "0XDECAFBAD"
    participant.case = case

    # Set up a default case costs type.
    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    case_cost_type.default = True
    case_cost_type.project = case.project

    # Set up case.
    case.case_type.cost_model.enabled = True
    case.case_type.cost_model.activities = [cost_model_activity]

    case.conversation = conversation
    case.dedicated_channel = True

    # Calculates and updates the case cost.
    cost = update_case_response_cost(case_id=case.id, db_session=session)
    activities = get_all_case_participant_activities_for_case(db_session=session, case_id=case.id)
    assert activities

    # Evaluate expected case cost.
    participants_total_response_time_seconds = timedelta(seconds=0)
    for activity in activities:
        participants_total_response_time_seconds += activity.ended_at - activity.started_at
    hourly_rate = get_hourly_rate(case.project)
    expected_case_cost = (
        math.ceil(
            (participants_total_response_time_seconds.seconds / SECONDS_IN_HOUR) * hourly_rate
        )
        + orig_total_case_cost
    )

    assert cost
    assert cost == expected_case_cost
    assert cost == case.total_cost


def test_calculate_case_response_cost__no_enabled_plugins(
    session,
    case,
    case_cost_type,
    cost_model_activity,
    plugin_instance,
    conversation,
    participant,
):
    """Tests that the case cost is calculated correctly when a cost model is enabled."""
    from dispatch.case.service import get
    from dispatch.case_cost.service import update_case_response_cost
    from dispatch.case_cost_type import service as case_cost_type_service
    from dispatch.participant_activity.service import (
        get_all_case_participant_activities_for_case,
    )

    # Disable the plugin instance for the cost model plugin event.
    plugin_instance.project_id = case.project.id
    plugin_instance.enabled = False
    cost_model_activity.plugin_event.plugin = plugin_instance.plugin
    participant.user_conversation_id = "0XDECAFBAD"
    participant.case = case

    # Set up a default case costs type.
    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    case_cost_type.default = True
    case_cost_type.project = case.project

    # Set up case.
    case = get(db_session=session, case_id=case.id)
    case.case_type.cost_model.enabled = True
    case.case_type.cost_model.activities = [cost_model_activity]
    case.conversation = conversation

    # Calculates and updates the case cost.
    cost = update_case_response_cost(case_id=case.id, db_session=session)
    activities = get_all_case_participant_activities_for_case(db_session=session, case_id=case.id)
    assert not activities
    assert not cost
    assert not case.total_cost


def test_update_case_response_cost__no_cost_model(case, session, case_cost_type):
    """Tests that the case response cost is not created if the case type has no cost model."""
    from dispatch.case import service as case_service
    from dispatch.case_cost.service import update_case_response_cost
    from dispatch.case_cost_type import service as case_cost_type_service

    # Set up a default case costs type.
    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    case_cost_type.default = True
    case_cost_type.project = case.project

    case = case_service.get(db_session=session, case_id=case.id)
    case.case_type.cost_model = None

    # The case response cost should not be created without a cost model.
    case_response_cost_amount = update_case_response_cost(case_id=case.id, db_session=session)

    assert not case_response_cost_amount


def test_update_case_response_cost__fail(case, session):
    """Tests that the case response cost is not created if the project has no default cost_type."""
    from dispatch.case import service as case_service
    from dispatch.case_cost.service import (
        update_case_response_cost,
        get_by_case_id,
    )
    from dispatch.case_cost_type import service as case_cost_type_service

    case = case_service.get(db_session=session, case_id=case.id)

    # Ensure there is no default cost type for this project.
    for cost_type in case_cost_type_service.get_all(db_session=session):
        cost_type.default = False

    # Fail to create the inital case response cost.
    assert not update_case_response_cost(case_id=case.id, db_session=session)

    # Validate that the case cost was not created nor saved in the database.
    assert not get_by_case_id(db_session=session, case_id=case.id)
