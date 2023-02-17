def test_get(session, signal_filter):
    from dispatch.signal.service import get_signal_filter

    t_signal_filter = get_signal_filter(db_session=session, signal_filter_id=signal_filter.id)
    assert t_signal_filter.id == signal_filter.id


def test_create(session, user, project):
    from dispatch.signal.service import create_signal_filter
    from dispatch.signal.models import SignalFilterCreate

    name = "name"
    description = "description"
    expression = [{}]

    signal_filter_in = SignalFilterCreate(
        name=name,
        description=description,
        expression=expression,
        project=project,
    )
    signal_filter = create_signal_filter(
        db_session=session, creator=user, signal_filter_in=signal_filter_in
    )
    assert signal_filter


def test_update(session, signal_filter):
    from dispatch.signal.service import update_signal_filter
    from dispatch.signal.models import SignalFilterUpdate

    name = "Updated name"

    signal_filter_in = SignalFilterUpdate(id=signal_filter.id, name=name, expression=[{}])
    signal_filter = update_signal_filter(
        db_session=session,
        signal_filter=signal_filter,
        signal_filter_in=signal_filter_in,
    )
    assert signal_filter.name == name


def test_delete(session, signal_filter):
    from dispatch.signal.service import delete_signal_filter, get_signal_filter

    delete_signal_filter(db_session=session, signal_filter_id=signal_filter.id)
    assert not get_signal_filter(db_session=session, signal_filter_id=signal_filter.id)
