def test_get(session, incident_cost):
    from dispatch.incident_cost.service import get

    t_incident_cost = get(db_session=session, incident_cost_id=incident_cost.id)
    assert t_incident_cost.id == incident_cost.id


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
    from dispatch.incident_cost.service import (
        update_incident_response_cost,
    )
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
    incident.cost_model.enabled = True
    incident.cost_model.activities = [cost_model_activity]
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
    hourly_rate = math.ceil(
        incident.project.annual_employee_cost / incident.project.business_year_hours
    )
    expected_incident_cost = (
        math.ceil(
            (participants_total_response_time_seconds.seconds / SECONDS_IN_HOUR) * hourly_rate
        )
        + orig_total_incident_cost
    )

    assert cost
    assert cost == expected_incident_cost == incident.total_cost
