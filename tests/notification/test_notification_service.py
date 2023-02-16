def test_get(session, notification):
    from dispatch.notification.service import get

    t_notification = get(db_session=session, notification_id=notification.id)
    assert t_notification.id == notification.id


def test_get_all(session, notifications):
    from dispatch.notification.service import get_all

    t_notifications = get_all(db_session=session).all()
    assert t_notifications


def test_create(session, project):
    from dispatch.notification.service import create
    from dispatch.notification.models import NotificationCreate

    name = "name"
    description = "description"
    type = "email"
    target = "target"
    enabled = True

    notification_in = NotificationCreate(
        name=name,
        description=description,
        type=type,
        target=target,
        enabled=enabled,
        project=project,
    )
    notification = create(db_session=session, notification_in=notification_in)
    assert notification


def test_update(session, notification):
    from dispatch.notification.service import update
    from dispatch.notification.models import NotificationUpdate

    name = "Updated name"
    target = "incident-channel"
    type = "conversation"

    notification_in = NotificationUpdate(name=name, target=target, type=type)
    notification = update(
        db_session=session,
        notification=notification,
        notification_in=notification_in,
    )
    assert notification.name == name


def test_delete(session, notification):
    from dispatch.notification.service import delete, get

    delete(db_session=session, notification_id=notification.id)
    assert not get(db_session=session, notification_id=notification.id)
