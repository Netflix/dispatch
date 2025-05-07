def test_get(session, notification):
    from dispatch.notification.service import get

    t_notification = get(db_session=session, notification_id=notification.id)
    assert t_notification is not None
    assert t_notification.id == notification.id


def test_get_all(session, notifications):
    from dispatch.notification.service import get_all

    t_notifications = get_all(db_session=session).all()
    assert t_notifications


def test_create(session, project):
    from dispatch.notification.service import create
    from dispatch.notification.models import NotificationCreate, NotificationTypeEnum
    from dispatch.project.models import ProjectRead

    name = "test_notification_name"
    description = "test_notification_description"
    notif_type = NotificationTypeEnum.email
    target = "test_target@example.com"
    enabled = True

    notification_in = NotificationCreate(
        name=name,
        description=description,
        type=notif_type,
        target=target,
        enabled=enabled,
        project=ProjectRead.model_validate(project),
        filters=[]
    )
    created_notification = create(db_session=session, notification_in=notification_in)
    assert created_notification is not None
    assert created_notification.name == name
    assert created_notification.type == notif_type.value
    assert created_notification.project.id == project.id


def test_update(session, notification, project):
    from dispatch.notification.service import update
    from dispatch.notification.models import NotificationUpdate, NotificationTypeEnum

    updated_name = "Updated name"
    updated_target = "incident-channel"
    updated_type = NotificationTypeEnum.conversation

    notification_in = NotificationUpdate(
        name=updated_name,
        target=updated_target,
        type=updated_type,
        description=notification.description,
        enabled=notification.enabled,
        filters=[]
    )
    updated_notification_obj = update(
        db_session=session,
        notification=notification,
        notification_in=notification_in,
    )
    assert updated_notification_obj is not None
    assert updated_notification_obj.name == updated_name
    assert updated_notification_obj.target == updated_target
    assert updated_notification_obj.type == updated_type.value


def test_delete(session, notification):
    from dispatch.notification.service import delete, get

    delete(db_session=session, notification_id=notification.id)
    assert not get(db_session=session, notification_id=notification.id)
