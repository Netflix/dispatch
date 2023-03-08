def test_create_signal_instance(session, signal, user):
    from dispatch.signal.flows import create_signal_instance

    instance_data = {"variant": signal.variant}

    assert create_signal_instance(
        db_session=session,
        project=signal.project,
        signal_instance_data=instance_data,
        current_user=user,
    )
