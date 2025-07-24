from datetime import datetime, timedelta, timezone


def test_get_signal_stats_basic(session, entity, entity_type, signal, signal_instance):
    """Test the basic functionality of get_signal_stats."""
    from dispatch.signal.service import get_signal_stats

    # Setup: Associate the entity with the signal instance
    entity.entity_type = entity_type
    signal_instance.entities.append(entity)
    signal_instance.signal = signal
    session.commit()

    # Execute: Call the service function
    signal_data = get_signal_stats(
        db_session=session,
        entity_value=entity.value,
        entity_type_id=entity_type.id,
        num_days=None,
    )

    # Assert: Check the result
    assert signal_data is not None
    assert signal_data.num_signal_instances_alerted >= 0
    assert signal_data.num_signal_instances_snoozed >= 0
    assert signal_data.num_snoozes_active >= 0
    assert signal_data.num_snoozes_expired >= 0


def test_get_signal_stats_with_num_days(session, entity, entity_type, signal, signal_instance):
    """Test get_signal_stats with the num_days parameter."""
    from dispatch.signal.service import get_signal_stats

    # Setup: Associate the entity with the signal instance
    entity.entity_type = entity_type
    signal_instance.entities.append(entity)
    signal_instance.signal = signal
    # Set created_at to a specific time for testing
    signal_instance.created_at = datetime.utcnow() - timedelta(days=3)
    session.commit()

    # Execute: Call the service function with num_days=7 (should include our instance)
    signal_data_7_days = get_signal_stats(
        db_session=session,
        entity_value=entity.value,
        entity_type_id=entity_type.id,
        num_days=7,
    )

    # Execute: Call the service function with num_days=1 (should exclude our instance)
    signal_data_1_day = get_signal_stats(
        db_session=session,
        entity_value=entity.value,
        entity_type_id=entity_type.id,
        num_days=1,
    )

    # Assert: Check the results
    assert signal_data_7_days is not None
    assert (
        signal_data_7_days.num_signal_instances_alerted
        + signal_data_7_days.num_signal_instances_snoozed
        > 0
    )

    assert signal_data_1_day is not None
    assert (
        signal_data_1_day.num_signal_instances_alerted
        + signal_data_1_day.num_signal_instances_snoozed
        == 0
    )


def test_get_signal_stats_with_snooze_filter(
    session, entity, entity_type, signal, signal_instance, signal_filter
):
    """Test get_signal_stats with a snooze filter applied."""
    from dispatch.signal.service import get_signal_stats
    from dispatch.signal.models import SignalFilterAction

    # Setup: Associate the entity with the signal instance and add a snooze filter
    entity.entity_type = entity_type
    signal_instance.entities.append(entity)
    signal_instance.signal = signal
    signal_instance.filter_action = SignalFilterAction.snooze

    # Create a snooze filter that's active
    signal_filter.action = SignalFilterAction.snooze
    signal_filter.expiration = datetime.now(timezone.utc) + timedelta(days=1)
    signal_filter.expression = [
        {"or": [{"model": "Entity", "field": "id", "op": "==", "value": entity.id}]}
    ]
    signal.filters.append(signal_filter)

    session.commit()

    # Execute: Call the service function
    signal_data = get_signal_stats(
        db_session=session,
        entity_value=entity.value,
        entity_type_id=entity_type.id,
        num_days=None,
    )

    # Assert: Check the result
    assert signal_data is not None
    assert signal_data.num_signal_instances_snoozed > 0
    assert signal_data.num_snoozes_active > 0


def test_get_signal_stats_with_expired_snooze_filter(
    session, entity, entity_type, signal, signal_instance, signal_filter
):
    """Test get_signal_stats with an expired snooze filter."""
    from dispatch.signal.service import get_signal_stats
    from dispatch.signal.models import SignalFilterAction

    # Setup: Associate the entity with the signal instance and add an expired snooze filter
    entity.entity_type = entity_type
    signal_instance.entities.append(entity)
    signal_instance.signal = signal

    # Create a snooze filter that's expired
    signal_filter.action = SignalFilterAction.snooze
    signal_filter.expiration = datetime.now(timezone.utc) - timedelta(days=1)
    signal_filter.expression = [
        {"or": [{"model": "Entity", "field": "id", "op": "==", "value": entity.id}]}
    ]
    signal.filters.append(signal_filter)

    session.commit()

    # Execute: Call the service function
    signal_data = get_signal_stats(
        db_session=session,
        entity_value=entity.value,
        entity_type_id=entity_type.id,
        num_days=None,
    )

    # Assert: Check the result
    assert signal_data is not None
    assert signal_data.num_snoozes_expired > 0


def test_get_signal_stats_not_found(session, entity_type):
    """Test get_signal_stats when no signals are found."""
    from dispatch.signal.service import get_signal_stats

    # Execute: Call the service function with a non-existent entity value
    signal_data = get_signal_stats(
        db_session=session,
        entity_value="non-existent-entity",
        entity_type_id=entity_type.id,
        num_days=None,
    )

    # Assert: Check the result
    assert signal_data is not None
    assert signal_data.num_signal_instances_alerted == 0
    assert signal_data.num_signal_instances_snoozed == 0
    assert signal_data.num_snoozes_active == 0
    assert signal_data.num_snoozes_expired == 0


def test_get_signal_stats_with_signal_id_filter(session, entity, entity_type):
    """Test get_signal_stats with a specific signal ID filter."""
    from dispatch.signal.service import get_signal_stats
    from dispatch.signal.models import Signal, SignalInstance

    # Setup: Create two different signals
    signal1 = Signal(name="Test Signal 1", variant="test-signal-1", project_id=1)
    signal2 = Signal(name="Test Signal 2", variant="test-signal-2", project_id=1)
    session.add_all([signal1, signal2])
    session.flush()

    # Associate entity with entity type
    entity.entity_type = entity_type

    # Create a signal instance for signal1
    signal_instance1 = SignalInstance(signal=signal1, project_id=1)
    signal_instance1.entities.append(entity)

    # Create two signal instances for signal2
    signal_instance2 = SignalInstance(signal=signal2, project_id=1)
    signal_instance2.entities.append(entity)
    signal_instance3 = SignalInstance(signal=signal2, project_id=1)
    signal_instance3.entities.append(entity)

    session.add_all([signal_instance1, signal_instance2, signal_instance3])
    session.commit()

    # Execute: Call the service function without signal_id (should count both signals)
    signal_data_all = get_signal_stats(
        db_session=session,
        entity_value=entity.value,
        entity_type_id=entity_type.id,
        num_days=None,
    )

    # Execute: Call the service function with signal_id for signal1
    signal_data_signal1 = get_signal_stats(
        db_session=session,
        entity_value=entity.value,
        entity_type_id=entity_type.id,
        signal_id=signal1.id,
        num_days=None,
    )

    # Execute: Call the service function with signal_id for signal2
    signal_data_signal2 = get_signal_stats(
        db_session=session,
        entity_value=entity.value,
        entity_type_id=entity_type.id,
        signal_id=signal2.id,
        num_days=None,
    )

    # Assert: Without signal_id filter, we should count both instances
    assert (
        signal_data_all.num_signal_instances_alerted + signal_data_all.num_signal_instances_snoozed
        == 3
    )

    # Assert: With signal1 filter, we should count only signal_instance1
    assert (
        signal_data_signal1.num_signal_instances_alerted
        + signal_data_signal1.num_signal_instances_snoozed
        == 1
    )

    # Assert: With signal2 filter, we should count only signal_instance2
    assert (
        signal_data_signal2.num_signal_instances_alerted
        + signal_data_signal2.num_signal_instances_snoozed
        == 2
    )
