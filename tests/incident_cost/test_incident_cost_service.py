import pytest


def test_get(session, incident_cost):
    from dispatch.incident_cost.service import get

    t_incident_cost = get(db_session=session, incident_cost_id=incident_cost.id)
    assert t_incident_cost.id == incident_cost.id


def test_get_all(session, incident_costs):
    from dispatch.incident_cost.service import get_all

    t_incident_costs = get_all(db_session=session).all()
    assert len(t_incident_costs) > 1


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


@pytest.mark.skip
def test_update(session, incident_cost):
    from dispatch.incident_cost.service import update
    from dispatch.incident_cost.models import IncidentCostUpdate

    amount = 10001

    incident_cost_in = IncidentCostUpdate(
        amount=amount,
    )
    incident_cost = update(
        db_session=session, incident_cost=incident_cost, incident_cost_in=incident_cost_in
    )
    assert incident_cost.amount == amount


def test_delete(session, incident_cost):
    from dispatch.incident_cost.service import delete, get

    delete(db_session=session, incident_cost_id=incident_cost.id)
    assert not get(db_session=session, incident_cost_id=incident_cost.id)
