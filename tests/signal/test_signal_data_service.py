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
