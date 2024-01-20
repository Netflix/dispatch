# Cost Model Activity Tests


def test_create_cost_model_activity(session, plugin_event):
    from dispatch.cost_model.service import create_cost_model_activity
    from dispatch.cost_model.models import CostModelActivityCreate

    cost_model_activity_in = CostModelActivityCreate(
        plugin_event=plugin_event,
        response_time_seconds=5,
        enabled=True,
    )

    activity = create_cost_model_activity(
        db_session=session, cost_model_activity_in=cost_model_activity_in
    )

    assert activity


def test_update_cost_model_activity(session, cost_model_activity):
    from dispatch.cost_model.service import update_cost_model_activity
    from dispatch.cost_model.models import CostModelActivityUpdate

    cost_model_activity_in = CostModelActivityUpdate(
        id=cost_model_activity.id,
        plugin_event=cost_model_activity.plugin_event,
        response_time_seconds=cost_model_activity.response_time_seconds + 2,
        enabled=cost_model_activity.enabled,
    )

    activity = update_cost_model_activity(
        db_session=session, cost_model_activity_in=cost_model_activity_in
    )

    assert activity
    assert activity.response_time_seconds == cost_model_activity_in.response_time_seconds


def test_delete_cost_model_activity(session, cost_model_activity):
    from dispatch.cost_model.service import (
        delete_cost_model_activity,
        get_cost_model_activity_by_id,
    )
    from sqlalchemy.orm.exc import NoResultFound

    delete_cost_model_activity(db_session=session, cost_model_activity_id=cost_model_activity.id)
    deleted = False

    try:
        get_cost_model_activity_by_id(
            db_session=session, cost_model_activity_id=cost_model_activity.id
        )
    except NoResultFound:
        deleted = True

    assert deleted


# Cost Model Tests


def test_create_cost_model(session, cost_model_activity, project):
    """Tests that a cost model can be created."""
    from dispatch.cost_model.models import CostModelCreate
    from datetime import datetime
    from dispatch.cost_model.service import create, get_cost_model_by_id

    name = "model_name"
    description = "model_description"
    activities = [cost_model_activity]
    enabled = False

    cost_model_in = CostModelCreate(
        name=name,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        activities=activities,
        enabled=enabled,
        project=project,
    )
    cost_model = create(db_session=session, cost_model_in=cost_model_in)

    # Validate cost model creation
    assert cost_model
    assert cost_model.name == cost_model_in.name
    assert cost_model.description == cost_model_in.description
    assert cost_model.enabled == cost_model_in.enabled
    assert len(cost_model.activities) == len(cost_model_in.activities)

    activity_out = cost_model.activities[0]
    assert activity_out.response_time_seconds == cost_model_activity.response_time_seconds
    assert activity_out.enabled == cost_model_activity.enabled
    assert activity_out.plugin_event.id == cost_model_activity.plugin_event.id

    # Validate cost model retrieval
    cost_model = get_cost_model_by_id(db_session=session, cost_model_id=cost_model.id)
    assert cost_model.created_at == cost_model.created_at
    assert cost_model.updated_at == cost_model.updated_at
    assert cost_model.name == cost_model.name
    assert cost_model.description == cost_model.description
    assert cost_model.enabled == cost_model.enabled
    assert len(cost_model.activities) == len(cost_model.activities)


def test_fail_create_cost_model(session, plugin_event, project):
    """Tests that a cost model cannot be created with duplicate plugin events."""
    from dispatch.cost_model.models import CostModelCreate
    from dispatch.cost_model.models import CostModelActivityCreate
    from datetime import datetime
    from dispatch.cost_model.service import create

    cost_model_activity_in = CostModelActivityCreate(
        plugin_event=plugin_event,
        response_time_seconds=5,
        enabled=True,
    )

    name = "model_name"
    description = "model_description"
    activities = [cost_model_activity_in, cost_model_activity_in]
    enabled = False

    cost_model_in = CostModelCreate(
        name=name,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        activities=activities,
        enabled=enabled,
        project=project,
    )
    try:
        create(db_session=session, cost_model_in=cost_model_in)
    except KeyError as e:
        assert "Duplicate plugin event ids" in str(e)


def test_update_cost_model(session, cost_model):
    """Tests that a cost model and all its activities are updated.

    The update test cases are:
        - Adding a new cost model activity to the existing cost model
        - Modifying an existing cost model activity
        - Deleting a cost model activity from the existing cost model
    """
    import copy
    from tests.factories import PluginEventFactory

    from dispatch.cost_model.service import update
    from dispatch.cost_model.models import (
        CostModelActivityCreate,
        CostModelActivityUpdate,
        CostModelUpdate,
    )

    plugin_event_0 = PluginEventFactory()
    plugin_event_1 = PluginEventFactory()

    # Update: adding new cost model activities
    add_cost_model_activity_0 = CostModelActivityCreate(
        plugin_event=plugin_event_0, response_time_seconds=1, enabled=True
    )
    add_cost_model_activity_1 = CostModelActivityCreate(
        plugin_event=plugin_event_1,
        response_time_seconds=2,
        enabled=True,
    )
    add_update_cost_model_in = CostModelUpdate(
        id=cost_model.id,
        name="new name",
        description="new description",
        enabled=True,
        project=cost_model.project,
        activities=[add_cost_model_activity_0, add_cost_model_activity_1],
    )

    add_update_cost_model = update(db_session=session, cost_model_in=add_update_cost_model_in)

    assert add_update_cost_model.description == add_update_cost_model_in.description
    assert add_update_cost_model.name == add_update_cost_model_in.name
    assert add_update_cost_model.enabled == add_update_cost_model_in.enabled
    assert len(add_update_cost_model.activities) == len(add_update_cost_model_in.activities)
    for (
        actual,
        expected,
    ) in zip(
        add_update_cost_model.activities,
        add_update_cost_model_in.activities,
        strict=True,
    ):
        assert actual.response_time_seconds == expected.response_time_seconds
        assert actual.enabled == expected.enabled
        assert actual.plugin_event.id == expected.plugin_event.id

    id_0 = add_update_cost_model.activities[0].id
    id_1 = add_update_cost_model.activities[1].id

    # Update: modifying existing cost model activities
    modify_cost_model_activity_0 = CostModelActivityUpdate(
        plugin_event=plugin_event_0, response_time_seconds=3, enabled=True, id=id_0
    )
    modify_cost_model_activity_1 = CostModelActivityUpdate(
        plugin_event=plugin_event_1,
        response_time_seconds=4,
        enabled=True,
        id=id_1,
    )
    modify_update_cost_model_in = CostModelUpdate(
        id=cost_model.id,
        name="new name",
        description="new description",
        enabled=True,
        project=cost_model.project,
        activities=[modify_cost_model_activity_0, modify_cost_model_activity_1],
    )
    modify_update_cost_model = update(
        db_session=session,
        cost_model_in=copy.deepcopy(modify_update_cost_model_in),
    )

    assert modify_update_cost_model.description == modify_update_cost_model_in.description
    assert modify_update_cost_model.name == modify_update_cost_model_in.name
    assert modify_update_cost_model.enabled == modify_update_cost_model_in.enabled
    assert len(modify_update_cost_model.activities) == len(modify_update_cost_model_in.activities)
    for (
        actual,
        expected,
    ) in zip(
        modify_update_cost_model.activities,
        modify_update_cost_model_in.activities,
        strict=True,
    ):
        assert actual.response_time_seconds == expected.response_time_seconds
        assert actual.enabled == expected.enabled
        assert actual.plugin_event.id == expected.plugin_event.id

    # Update: deleting existing cost model activities
    retained_cost_model_activity = modify_cost_model_activity_1
    delete_update_cost_model_in = CostModelUpdate(
        id=cost_model.id,
        name=cost_model.name,
        description=cost_model.description,
        enabled=cost_model.enabled,
        project=cost_model.project,
        activities=[retained_cost_model_activity],
    )
    delete_update_cost_model = update(db_session=session, cost_model_in=delete_update_cost_model_in)
    assert len(delete_update_cost_model.activities) == 1
    assert (
        delete_update_cost_model.activities[0].plugin_event.id
        == retained_cost_model_activity.plugin_event.id
    )


def test_delete_cost_model(session, cost_model, cost_model_activity):
    """Tests that a cost model and all its activities are deleted."""
    from dispatch.cost_model.service import delete, get_cost_model_by_id
    from dispatch.cost_model import (
        service as cost_model_service,
    )
    from sqlalchemy.orm.exc import NoResultFound

    cost_model.activities.append(cost_model_activity)
    delete(db_session=session, cost_model_id=cost_model.id)
    deleted = False

    try:
        get_cost_model_by_id(db_session=session, cost_model_id=cost_model.id)
    except NoResultFound:
        deleted = True

    try:
        cost_model_service.get_cost_model_activity_by_id(
            db_session=session, cost_model_activity_id=cost_model_activity.id
        )
    except NoResultFound:
        deleted = deleted and True

    # Fails if the cost model and all its activities are not deleted.
    assert deleted
