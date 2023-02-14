import pytest


def test_get(session, signal):
    from dispatch.signal.service import get

    t_signal = get(db_session=session, signal_id=signal.id)
    assert t_signal.id == signal.id


def test_get_instance(session, signal_instance):
    from dispatch.signal.service import get_instance

    t_signal_instance = get_instance(db_session=session, signal_instance_id=signal_instance.id)
    assert t_signal_instance.id == signal_instance.id


def test_create_instance(session, signal, project):
    from dispatch.signal.service import create_instance
    from dispatch.signal.models import SignalInstanceCreate

    signal_instance_in = SignalInstanceCreate(
        enabled=enabled,
        configuration=configuration,
        signal=signal,
        project=project,
    )
    signal_instance = create_instance(db_session=session, signal_instance_in=signal_instance_in)
    assert signal_instance
