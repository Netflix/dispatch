# Incident Cost Model Activity Tests


def test_create_incident_cost_model_activity(session, plugin_event):
    from dispatch.incident_cost_model.service import create_incident_cost_model_activity
    from dispatch.incident_cost_model.models import IncidentCostModelActivityCreate

    incident_cost_model_activity_in = IncidentCostModelActivityCreate(
        plugin_event=plugin_event,
        response_time_seconds=5,
        enabled=True,
    )

    activity = create_incident_cost_model_activity(
        db_session=session, incident_cost_model_activity_in=incident_cost_model_activity_in
    )

    assert activity


def test_update_incident_cost_model_activity(session, incident_cost_model_activity):
    from dispatch.incident_cost_model.service import update_incident_cost_model_activity
    from dispatch.incident_cost_model.models import IncidentCostModelActivityUpdate

    incident_cost_model_activity_in = IncidentCostModelActivityUpdate(
        id=incident_cost_model_activity.id,
        plugin_event=incident_cost_model_activity.plugin_event,
        response_time_seconds=incident_cost_model_activity.response_time_seconds + 2,
        enabled=incident_cost_model_activity.enabled,
    )

    activity = update_incident_cost_model_activity(
        db_session=session, incident_cost_model_activity_in=incident_cost_model_activity_in
    )

    assert activity
    assert activity.response_time_seconds == incident_cost_model_activity_in.response_time_seconds


def test_delete_incident_cost_model_activity(session, incident_cost_model_activity):
    from dispatch.incident_cost_model.service import (
        delete_incident_cost_model_activity,
        get_incident_cost_model_activity_by_id,
    )
    from sqlalchemy.orm.exc import NoResultFound

    delete_incident_cost_model_activity(
        db_session=session, incident_cost_model_activity_id=incident_cost_model_activity.id
    )
    deleted = False

    try:
        get_incident_cost_model_activity_by_id(
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
    assert activity_out.plugin_event.id == incident_cost_model_activity.plugin_event.id

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
    from dispatch.incident_cost_model.models import IncidentCostModelActivityCreate
    from datetime import datetime
    from dispatch.incident_cost_model.service import create

    incident_cost_model_activity_in = IncidentCostModelActivityCreate(
        plugin_event=plugin_event,
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
        create(db_session=session, incident_cost_model_in=incident_cost_model_in)
    except KeyError as e:
        assert "Duplicate plugin event ids" in str(e)


def test_update_cost_model(
    session, incident_cost_model, incident_cost_model_activity, plugin_event
):
    import copy
    from dispatch.incident_cost_model.service import update
    from dispatch.incident_cost_model.models import (
        IncidentCostModelActivityCreate,
        IncidentCostModelActivityUpdate,
        IncidentCostModelUpdate,
    )

    # Update: adding new cost model activities
    add_incident_cost_model_activity_0 = IncidentCostModelActivityCreate(
        plugin_event=plugin_event, response_time_seconds=1, enabled=True
    )
    add_incident_cost_model_activity_1 = IncidentCostModelActivityCreate(
        plugin_event=incident_cost_model_activity.plugin_event,
        response_time_seconds=2,
        enabled=True,
    )
    add_update_incident_cost_model_in = IncidentCostModelUpdate(
        id=incident_cost_model.id,
        name="new name",
        description="new description",
        enabled=True,
        project=incident_cost_model.project,
        activities=[add_incident_cost_model_activity_0, add_incident_cost_model_activity_1],
    )

    add_update_incident_cost_model = update(
        db_session=session, incident_cost_model_in=add_update_incident_cost_model_in
    )

    assert (
        add_update_incident_cost_model.description == add_update_incident_cost_model_in.description
    )
    assert add_update_incident_cost_model.name == add_update_incident_cost_model_in.name
    assert add_update_incident_cost_model.enabled == add_update_incident_cost_model_in.enabled
    assert len(add_update_incident_cost_model.activities) == len(
        add_update_incident_cost_model_in.activities
    )
    for (
        actual,
        expected,
    ) in zip(
        add_update_incident_cost_model.activities,
        add_update_incident_cost_model_in.activities,
        strict=True,
    ):
        assert actual.response_time_seconds == expected.response_time_seconds
        assert actual.enabled == expected.enabled
        assert actual.plugin_event.id == expected.plugin_event.id

    id_0 = add_update_incident_cost_model.activities[0].id
    id_1 = add_update_incident_cost_model.activities[1].id

    # Update: modifying existing cost model activities
    modify_incident_cost_model_activity_0 = IncidentCostModelActivityUpdate(
        plugin_event=plugin_event, response_time_seconds=3, enabled=True, id=id_0
    )
    modify_incident_cost_model_activity_1 = IncidentCostModelActivityUpdate(
        plugin_event=incident_cost_model_activity.plugin_event,
        response_time_seconds=4,
        enabled=True,
        id=id_1,
    )
    modify_update_incident_cost_model_in = IncidentCostModelUpdate(
        id=incident_cost_model.id,
        name="new name",
        description="new description",
        enabled=True,
        project=incident_cost_model.project,
        activities=[modify_incident_cost_model_activity_0, modify_incident_cost_model_activity_1],
    )
    modify_update_incident_cost_model = update(
        db_session=session,
        incident_cost_model_in=copy.deepcopy(modify_update_incident_cost_model_in),
    )

    assert (
        modify_update_incident_cost_model.description
        == modify_update_incident_cost_model_in.description
    )
    assert modify_update_incident_cost_model.name == modify_update_incident_cost_model_in.name
    assert modify_update_incident_cost_model.enabled == modify_update_incident_cost_model_in.enabled
    assert len(modify_update_incident_cost_model.activities) == len(
        modify_update_incident_cost_model_in.activities
    )
    for (
        actual,
        expected,
    ) in zip(
        modify_update_incident_cost_model.activities,
        modify_update_incident_cost_model_in.activities,
        strict=True,
    ):
        assert actual.response_time_seconds == expected.response_time_seconds
        assert actual.enabled == expected.enabled
        assert actual.plugin_event.id == expected.plugin_event.id

    # Update: deleting existing cost model activities
    retained_incident_cost_model_activity = modify_incident_cost_model_activity_1
    delete_update_incident_cost_model_in = IncidentCostModelUpdate(
        id=incident_cost_model.id,
        name=incident_cost_model.name,
        description=incident_cost_model.description,
        enabled=incident_cost_model.enabled,
        project=incident_cost_model.project,
        activities=[retained_incident_cost_model_activity],
    )
    delete_update_incident_cost_model = update(
        db_session=session, incident_cost_model_in=delete_update_incident_cost_model_in
    )
    assert len(delete_update_incident_cost_model.activities) == 1
    assert (
        delete_update_incident_cost_model.activities[0].plugin_event.id
        == retained_incident_cost_model_activity.plugin_event.id
    )


def test_delete_cost_model(session, incident_cost_model, incident_cost_model_activity):
    from dispatch.incident_cost_model.service import delete, get_cost_model_by_id
    from dispatch.incident_cost_model import (
        service as incident_cost_model_service,
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
        incident_cost_model_service.get_incident_cost_model_activity_by_id(
            db_session=session, incident_cost_model_activity_id=incident_cost_model_activity.id
        )
    except NoResultFound:
        deleted = deleted and True

    # Fails if the cost model and all its activities are not deleted.
    assert deleted
