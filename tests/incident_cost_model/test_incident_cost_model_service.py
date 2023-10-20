# Incident Cost Model Activity Tests


def test_create_incident_cost_model_activity(session, plugin_event):
    from dispatch.incident_cost_model_activity.service import create_cost_model_activity
    from dispatch.incident_cost_model_activity.models import IncidentCostModelActivityCreate

    incident_cost_model_activity_in = IncidentCostModelActivityCreate(
        event=plugin_event,
        response_time_seconds=5,
        enabled=True,
    )

    activity = create_cost_model_activity(
        db_session=session, incident_cost_model_activity_in=incident_cost_model_activity_in
    )

    assert activity


def test_update_incident_cost_model_activity(session, incident_cost_model_activity):
    from dispatch.incident_cost_model_activity.service import create_cost_model_activity, update
    from dispatch.incident_cost_model_activity.models import IncidentCostModelActivityUpdate

    incident_cost_model_activity_in = IncidentCostModelActivityUpdate(
        id=incident_cost_model_activity.id,
        event=incident_cost_model_activity.event,
        response_time_seconds=incident_cost_model_activity.response_time_seconds + 2,
        enabled=incident_cost_model_activity.enabled,
    )

    activity = update(
        db_session=session, incident_cost_model_activity_in=incident_cost_model_activity_in
    )

    assert activity
    assert activity.response_time_seconds == incident_cost_model_activity_in.response_time_seconds


def test_delete_incident_cost_model_activity(session, incident_cost_model_activity):
    from dispatch.incident_cost_model_activity.service import delete, get_by_id
    from sqlalchemy.orm.exc import NoResultFound

    delete(db_session=session, incident_cost_model_activity_id=incident_cost_model_activity.id)
    deleted = False

    try:
        get_by_id(
            db_session=session, incident_cost_model_activity_id=incident_cost_model_activity.id
        )
    except NoResultFound:
        deleted = True

    assert deleted


# Incident Cost Model Tests


def test_create_incident_cost_model(session, incident_cost_model_activity, project):
    from dispatch.incident_cost_model.models import IncidentCostModelCreate
    from datetime import datetime
    from dispatch.incident_cost_model.service import create, get_cost_model_by_id

    name = "model_name"
    description = "model_description"
    activities = [incident_cost_model_activity]
    enabled = False

    incident_cost_model_in = IncidentCostModelCreate(
        name=name,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        activities=activities,
        enabled=enabled,
        project=project,
    )
    incident_cost_model = create(db_session=session, incident_cost_model_in=incident_cost_model_in)

    # Validate cost model creation
    assert incident_cost_model
    assert incident_cost_model.name == incident_cost_model_in.name
    assert incident_cost_model.description == incident_cost_model_in.description
    assert incident_cost_model.enabled == incident_cost_model_in.enabled
    assert len(incident_cost_model.activities) == len(incident_cost_model_in.activities)

    activity_out = incident_cost_model.activities[0]
    assert activity_out.response_time_seconds == incident_cost_model_activity.response_time_seconds
    assert activity_out.enabled == incident_cost_model_activity.enabled
    assert activity_out.event.id == incident_cost_model_activity.event.id

    # Validate cost model retrieval
    cost_model = get_cost_model_by_id(
        db_session=session, incident_cost_model_id=incident_cost_model.id
    )
    assert incident_cost_model.created_at == cost_model.created_at
    assert incident_cost_model.updated_at == cost_model.updated_at
    assert incident_cost_model.name == cost_model.name
    assert incident_cost_model.description == cost_model.description
    assert incident_cost_model.enabled == cost_model.enabled
    assert len(incident_cost_model.activities) == len(cost_model.activities)


def test_fail_create_incident_cost_model(session, plugin_event, project):
    """Tests that an incident cost model cannot be created with duplicate plugin events."""
    from dispatch.incident_cost_model.models import IncidentCostModelCreate
    from dispatch.incident_cost_model_activity.models import IncidentCostModelActivityCreate
    from datetime import datetime
    from dispatch.incident_cost_model.service import create, get_cost_model_by_id

    incident_cost_model_activity_in = IncidentCostModelActivityCreate(
        event=plugin_event,
        response_time_seconds=5,
        enabled=True,
    )

    name = "model_name"
    description = "model_description"
    activities = [incident_cost_model_activity_in, incident_cost_model_activity_in]
    enabled = False

    incident_cost_model_in = IncidentCostModelCreate(
        name=name,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        activities=activities,
        enabled=enabled,
        project=project,
    )
    try:
        incident_cost_model = create(
            db_session=session, incident_cost_model_in=incident_cost_model_in
        )
    except KeyError as e:
        assert "Duplicate event ids" in str(e)


def test_update_cost_model(session, incident_cost_model, incident_cost_model_activity):
    from dispatch.incident_cost_model.service import update

    incident_cost_model.activities.append(incident_cost_model_activity)
    incident_cost_model.description = "new description"
    incident_cost_model.name == "new name"
    incident_cost_model.enabled == True

    updated_cost_model = update(db_session=session, incident_cost_model_in=incident_cost_model)

    assert updated_cost_model.description == incident_cost_model.description
    assert updated_cost_model.name == incident_cost_model.name
    assert updated_cost_model.enabled == incident_cost_model.enabled
    assert len(updated_cost_model.activities) == len(updated_cost_model.activities)
    for (
        actual,
        expected,
    ) in zip(updated_cost_model.activities, incident_cost_model.activities):
        assert actual.response_time_seconds == expected.response_time_seconds
        assert actual.enabled == expected.enabled
        assert actual.event.id == expected.event.id


def test_delete_cost_model(session, incident_cost_model, incident_cost_model_activity):
    from dispatch.incident_cost_model.service import delete, get_cost_model_by_id
    from dispatch.incident_cost_model_activity import (
        service as incident_cost_model_activity_service,
    )
    from sqlalchemy.orm.exc import NoResultFound

    incident_cost_model.activities.append(incident_cost_model_activity)
    delete(db_session=session, incident_cost_model_id=incident_cost_model.id)
    deleted = False

    try:
        get_cost_model_by_id(db_session=session, incident_cost_model_id=incident_cost_model.id)
    except NoResultFound:
        deleted = True

    try:
        incident_cost_model_activity_service.get_by_id(
            db_session=session, incident_cost_model_activity_id=incident_cost_model_activity.id
        )
    except NoResultFound:
        deleted = deleted and True

    # One or more items were not deleted.
    assert deleted
