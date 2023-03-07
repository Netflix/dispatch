import json


def test_get(session, signal):
    from dispatch.signal.service import get

    t_signal = get(db_session=session, signal_id=signal.id)
    assert t_signal.id == signal.id


def test_create(session, project):
    from dispatch.signal.models import SignalCreate
    from dispatch.signal.service import create

    name = "name"
    description = "description"

    signal_in = SignalCreate(
        name=name,
        owner="example@test.com",
        external_id="foo",
        description=description,
        project=project,
    )
    signal = create(db_session=session, signal_in=signal_in)
    assert signal


def test_update(session, project, signal):
    from dispatch.signal.models import SignalUpdate
    from dispatch.signal.service import update

    name = "Updated name"

    signal_in = SignalUpdate(
        id=signal.id, name=name, project=project, owner="example.com", external_id="foo"
    )
    signal = update(
        db_session=session,
        signal=signal,
        signal_in=signal_in,
    )
    assert signal.name == name


def test_delete(session, signal):
    from dispatch.signal.service import delete, get

    delete(db_session=session, signal_id=signal.id)
    assert not get(db_session=session, signal_id=signal.id)


# instance tests
def test_create_instance(session, case, signal, project):
    from dispatch.signal.models import SignalInstanceCreate
    from dispatch.signal.service import create_instance

    signal_instance_in = SignalInstanceCreate(
        raw={"id": "foo"},
        project=project,
    )
    signal_instance = create_instance(db_session=session, signal_instance_in=signal_instance_in)
    assert signal_instance


def test_filter_actions_deduplicate(session, signal, project):
    from dispatch.signal.models import (
        SignalFilter,
        SignalInstance,
        SignalFilterAction,
    )
    from dispatch.signal.service import apply_filter_actions
    from dispatch.entity_type.models import EntityType
    from dispatch.entity.models import Entity

    entity_type = EntityType(
        name="test",
        field="id",
        regular_expression=None,
        project=project,
    )
    session.add(entity_type)

    entity = Entity(name="test", description="test", value="foo", entity_type=entity_type)
    session.add(entity)

    # create instance
    signal_instance_1 = SignalInstance(
        raw=json.dumps({"id": "foo"}), project=project, signal=signal, entities=[entity]
    )
    session.add(signal_instance_1)

    signal_instance_2 = SignalInstance(
        raw=json.dumps({"id": "foo"}), project=project, signal=signal, entities=[entity]
    )
    session.add(signal_instance_2)
    signal.entity_types.append(entity_type)

    session.commit()

    # create deduplicate signal filter
    signal_filter = SignalFilter(
        name="test",
        description="test",
        expression=[
            {"or": [{"model": "EntityType", "field": "id", "op": "==", "value": entity_type.id}]}
        ],
        action=SignalFilterAction.deduplicate,
        window=5,
        project=project,
    )
    signal.filters.append(signal_filter)

    session.commit()
    assert not apply_filter_actions(db_session=session, signal_instance=signal_instance_2)
    assert signal_instance_2.filter_action == SignalFilterAction.deduplicate


def test_filter_actions_snooze(session, signal, project):
    from datetime import datetime, timedelta, timezone
    from dispatch.signal.models import (
        SignalFilter,
        SignalInstance,
        SignalFilterAction,
    )
    from dispatch.signal.service import apply_filter_actions
    from dispatch.entity_type.models import EntityType
    from dispatch.entity.models import Entity

    entity_type = EntityType(
        name="test",
        field="id",
        regular_expression=None,
        project=project,
    )
    session.add(entity_type)
    signal.entity_types.append(entity_type)

    entity = Entity(name="test", description="test", value="foo", entity_type=entity_type)
    session.add(entity)

    # create instance
    signal_instance_1 = SignalInstance(
        raw=json.dumps({"id": "foo"}), project=project, signal=signal, entities=[entity]
    )
    session.add(signal_instance_1)
    session.commit()

    signal_filter = SignalFilter(
        name="snooze0",
        description="test",
        expression=[{"or": [{"model": "Entity", "field": "id", "op": "==", "value": entity.id}]}],
        action=SignalFilterAction.snooze,
        expiration=datetime.now(tz=timezone.utc) + timedelta(minutes=5),
        project=project,
    )

    signal.filters = [signal_filter]

    session.commit()
    assert not apply_filter_actions(db_session=session, signal_instance=signal_instance_1)
    assert signal_instance_1.filter_action == SignalFilterAction.snooze


def test_filter_actions_snooze_expired(session, signal, project):
    from datetime import datetime, timedelta, timezone
    from dispatch.signal.models import (
        SignalFilter,
        SignalInstance,
        SignalFilterAction,
    )
    from dispatch.signal.service import apply_filter_actions
    from dispatch.entity_type.models import EntityType
    from dispatch.entity.models import Entity

    entity_type = EntityType(
        name="test",
        field="id",
        regular_expression=None,
        project=project,
    )
    session.add(entity_type)

    entity = Entity(name="test", description="test", value="foo", entity_type=entity_type)
    session.add(entity)

    # create instance
    signal_instance_1 = SignalInstance(
        raw=json.dumps({"id": "foo"}), project=project, signal=signal, entities=[entity]
    )
    session.add(signal_instance_1)

    # expired
    signal_filter = SignalFilter(
        name="snooze1",
        description="test",
        expression=[{"or": [{"model": "Entity", "field": "id", "op": "==", "value": 1}]}],
        action=SignalFilterAction.snooze,
        expiration=datetime.now(timezone.utc) - timedelta(minutes=5),
        project=project,
    )

    signal.filters = [signal_filter]
    session.commit()
    assert apply_filter_actions(db_session=session, signal_instance=signal_instance_1)
