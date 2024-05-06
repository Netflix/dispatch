def test_get(session, incident_cost):
    from dispatch.incident_cost.service import get

    t_incident_cost = get(db_session=session, incident_cost_id=incident_cost.id)
    assert t_incident_cost.id == incident_cost.id


def test_get_by_incident_id(session, incident_cost):
    from dispatch.incident_cost.service import get_by_incident_id

    assert get_by_incident_id(db_session=session, incident_id=incident_cost.incident_id)


def test_get_all(session, incident_costs):
    from dispatch.incident_cost.service import get_all

    t_incident_costs = get_all(db_session=session).all()
    assert t_incident_costs


def test_create(session, incident_cost_type, project):
    from dispatch.incident_cost.service import create
    from dispatch.incident_cost.models import IncidentCostCreate

    amount = 10000

    incident_cost_in = IncidentCostCreate(
        amount=amount,
        incident_cost_type=incident_cost_type,
        project=project,
    )
    incident_cost = create(db_session=session, incident_cost_in=incident_cost_in)
    assert incident_cost


def test_get_or_create__create(session, incident_cost_type, project):
    from dispatch.incident_cost.service import get_or_create
    from dispatch.incident_cost.models import IncidentCostCreate

    amount = 10000

    incident_cost_in = IncidentCostCreate(
        amount=amount,
        incident_cost_type=incident_cost_type,
        project=project,
    )
    incident_cost = get_or_create(db_session=session, incident_cost_in=incident_cost_in)
    assert incident_cost


def test_update(session, incident_cost, incident_cost_type):
    from dispatch.incident_cost.service import update
    from dispatch.incident_cost.models import IncidentCostUpdate

    amount = 10001

    incident_cost_in = IncidentCostUpdate(amount=amount, incident_cost_type=incident_cost_type)
    incident_cost = update(
        db_session=session, incident_cost=incident_cost, incident_cost_in=incident_cost_in
    )
    assert incident_cost.amount == amount


def test_delete(session, incident_cost):
    from dispatch.incident_cost.service import delete, get

    delete(db_session=session, incident_cost_id=incident_cost.id)
    assert not get(db_session=session, incident_cost_id=incident_cost.id)


def test_fetch_incident_event__enabled_plugins(
    incident,
    cost_model_activity,
    session,
    conversation_plugin_instance,
):
    from dispatch.incident_cost.service import fetch_incident_events

    conversation_plugin_instance.project_id = incident.project.id
    cost_model_activity.plugin_event.plugin = conversation_plugin_instance.plugin
    conversation_plugin_instance.enabled = True

    assert fetch_incident_events(incident, cost_model_activity, oldest="0", db_session=session)


def test_fetch_incident_event__no_enabled_plugins(
    incident,
    cost_model_activity,
    session,
    conversation_plugin_instance,
):
    from dispatch.incident_cost.service import fetch_incident_events

    conversation_plugin_instance.project_id = incident.project.id
    cost_model_activity.plugin_event.plugin = conversation_plugin_instance.plugin
    conversation_plugin_instance.enabled = False

    assert not fetch_incident_events(incident, cost_model_activity, oldest="0", db_session=session)


def test_calculate_incident_response_cost_with_cost_model(
    session,
    incident,
    incident_cost_type,
    cost_model_activity,
    conversation_plugin_instance,
    conversation,
    participant,
):
    """Tests that the incident cost is calculated correctly when a cost model is enabled."""
    from datetime import timedelta
    import math
    from dispatch.incident.service import get
    from dispatch.incident_cost.service import update_incident_response_cost, get_hourly_rate
    from dispatch.incident_cost_type import service as incident_cost_type_service
    from dispatch.participant_activity.service import (
        get_all_incident_participant_activities_for_incident,
    )
    from dispatch.plugins.dispatch_slack.events import ChannelActivityEvent

    SECONDS_IN_HOUR = 3600
    orig_total_incident_cost = incident.total_cost

    # Set incoming plugin events.
    conversation_plugin_instance.project_id = incident.project.id
    cost_model_activity.plugin_event.plugin = conversation_plugin_instance.plugin
    participant.user_conversation_id = "0XDECAFBAD"
    participant.incident = incident

    # Set up a default incident costs type.
    for cost_type in incident_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    incident_cost_type.default = True
    incident_cost_type.project = incident.project

    # Set up incident.
    incident = get(db_session=session, incident_id=incident.id)
    cost_model_activity.plugin_event.slug = ChannelActivityEvent.slug
    incident.incident_type.cost_model.enabled = True
    incident.incident_type.cost_model.activities = [cost_model_activity]
    incident.conversation = conversation

    # Calculates and updates the incident cost.
    cost = update_incident_response_cost(incident_id=incident.id, db_session=session)
    activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident.id
    )
    assert activities

    # Evaluate expected incident cost.
    participants_total_response_time_seconds = timedelta(seconds=0)
    for activity in activities:
        participants_total_response_time_seconds += activity.ended_at - activity.started_at
    hourly_rate = get_hourly_rate(incident.project)
    expected_incident_cost = (
        math.ceil(
            (participants_total_response_time_seconds.seconds / SECONDS_IN_HOUR) * hourly_rate
        )
        + orig_total_incident_cost
    )

    assert cost
    assert cost == expected_incident_cost
    assert cost == incident.total_cost


def test_calculate_incident_response_cost_with_cost_model__no_enabled_plugins(
    session,
    incident,
    incident_cost_type,
    cost_model_activity,
    plugin_instance,
    conversation,
    participant,
):
    """Tests that the incident cost is calculated correctly when a cost model is enabled."""
    from dispatch.incident.service import get
    from dispatch.incident_cost.service import update_incident_response_cost
    from dispatch.incident_cost_type import service as incident_cost_type_service
    from dispatch.participant_activity.service import (
        get_all_incident_participant_activities_for_incident,
    )

    # Disable the plugin instance for the cost model plugin event.
    plugin_instance.project_id = incident.project.id
    plugin_instance.enabled = False
    cost_model_activity.plugin_event.plugin = plugin_instance.plugin
    participant.user_conversation_id = "0XDECAFBAD"
    participant.incident = incident

    # Set up a default incident costs type.
    for cost_type in incident_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    incident_cost_type.default = True
    incident_cost_type.project = incident.project

    # Set up incident.
    incident = get(db_session=session, incident_id=incident.id)
    incident.incident_type.cost_model.enabled = True
    incident.incident_type.cost_model.activities = [cost_model_activity]
    incident.conversation = conversation

    # Calculates and updates the incident cost.
    cost = update_incident_response_cost(incident_id=incident.id, db_session=session)
    activities = get_all_incident_participant_activities_for_incident(
        db_session=session, incident_id=incident.id
    )
    assert not activities
    assert not cost
    assert not incident.total_cost


def test_calculate_incident_response_cost_without_cost_model(
    incident, session, incident_cost_type, participant_role, participant
):
    """Tests that the incident response cost is created and calculated correctly with the classic cost model."""
    from datetime import timedelta, datetime, UTC
    from dispatch.incident_cost.service import calculate_incident_response_cost_with_classic_model
    from dispatch.incident_cost_type import service as incident_cost_type_service

    # Set up a default incident costs type.
    for cost_type in incident_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    incident_cost_type.default = True
    incident_cost_type.project = incident.project

    # Set up timestamps
    incident.created_at = (datetime.now(UTC) - timedelta(hours=1)).replace(tzinfo=None)

    # Set up incident participants
    participant_role.participant = participant
    participant_role.activity = 1
    participant_role.assumed_at = (datetime.now(UTC) - timedelta(hours=1)).replace(tzinfo=None)
    incident.participants.append(participant_role.participant)

    updated_incident_cost = calculate_incident_response_cost_with_classic_model(
        incident=incident, db_session=session, incident_review=False
    )

    assert updated_incident_cost


def test_calculate_incident_response_cost_without_cost_model__update_cost(
    incident, session, incident_cost_type, participant_role, participant, incident_cost
):
    """Tests that the incident response cost is updated correctly with the classic cost model."""
    from datetime import timedelta, datetime, UTC

    from dispatch.incident import service as incident_service
    from dispatch.incident_cost.service import (
        calculate_incident_response_cost_with_classic_model,
    )
    from dispatch.incident_cost_type import service as incident_cost_type_service

    incident = incident_service.get(db_session=session, incident_id=incident.id)

    # Use a large annual_employee_cost to make the incident cost updates more noticeable.
    incident.project.annual_employee_cost = 100000000

    # Set up a default incident costs type.
    for cost_type in incident_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    incident_cost_type.default = True
    incident_cost_type.project = incident.project

    # Set up timestamps
    incident.created_at = (datetime.now(UTC) - timedelta(hours=1)).replace(tzinfo=None)

    # Create initial incident response cost.
    incident_cost.incident_cost_type = incident_cost_type
    incident_cost.incident = incident

    # Set up incident participants.
    participant_role.participant = participant
    participant_role.activity = 1
    participant_role.assumed_at = (datetime.now(UTC) - timedelta(hours=1)).replace(tzinfo=None)
    incident.participants.append(participant_role.participant)

    initial_incident_cost = incident_cost.amount

    updated_incident_cost = calculate_incident_response_cost_with_classic_model(
        incident=incident, db_session=session, incident_review=False
    )

    assert updated_incident_cost
    assert initial_incident_cost < updated_incident_cost


def test_update_incident_response_cost(incident, session, incident_cost_type):
    from dispatch.incident import service as incident_service
    from dispatch.incident_cost.service import (
        update_incident_response_cost,
        get_by_incident_id_and_incident_cost_type_id,
        get_hourly_rate,
    )
    from dispatch.incident_cost_type import service as incident_cost_type_service

    # Set up a default incident costs type.
    for cost_type in incident_cost_type_service.get_all(db_session=session):
        cost_type.default = False
    incident_cost_type.default = True
    incident_cost_type.project = incident.project

    incident = incident_service.get(db_session=session, incident_id=incident.id)
    incident.incident_type.cost_model = None

    # Create the inital incident response cost.
    incident_response_cost = update_incident_response_cost(
        incident_id=incident.id, db_session=session, incident_review=False
    )

    # Validate incident cost retrieval.
    t_incident_response_cost = get_by_incident_id_and_incident_cost_type_id(
        db_session=session, incident_id=incident.id, incident_cost_type_id=incident_cost_type.id
    )
    assert t_incident_response_cost
    assert t_incident_response_cost.amount == incident_response_cost

    # Add the incident review cost to the incident response cost.
    incident_review_cost = update_incident_response_cost(
        incident_id=incident.id, db_session=session, incident_review=True
    )

    # Validate the cost of the incident review.
    # With 1 participant, the incident review cost should be equal to the hourly rate.
    assert incident_review_cost == incident_response_cost + get_hourly_rate(incident.project)


def test_update_incident_response_cost__fail(incident, session):
    """Tests that the incident response cost is not created if the project has no default cost_type."""
    from dispatch.incident import service as incident_service
    from dispatch.incident_cost.service import (
        update_incident_response_cost,
        get_by_incident_id,
    )
    from dispatch.incident_cost_type import service as incident_cost_type_service

    incident = incident_service.get(db_session=session, incident_id=incident.id)

    # Ensure there is no default cost type for this project.
    for cost_type in incident_cost_type_service.get_all(db_session=session):
        cost_type.default = False

    # Fail to create the inital incident response cost.
    assert not update_incident_response_cost(
        incident_id=incident.id, db_session=session, incident_review=False
    )

    # Validate that the incident cost was not created nor saved in the database.
    assert not get_by_incident_id(db_session=session, incident_id=incident.id)
