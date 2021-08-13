def test_get(session, group):
    from dispatch.group.service import get

    t_group = get(db_session=session, group_id=group.id)
    assert t_group.id == group.id


def test_get_all(session, groups):
    from dispatch.group.service import get_all

    t_groups = get_all(db_session=session).all()
    assert t_groups


def test_create(session):
    from dispatch.group.service import create
    from dispatch.group.models import GroupCreate

    name = "XXX"
    email = "john.smith@example.org"
    resource_id = "XXX"
    resource_type = "XXX"
    weblink = "https://example.com/"

    group_in = GroupCreate(
        name=name,
        email=email,
        resource_id=resource_id,
        resource_type=resource_type,
        weblink=weblink,
    )
    group = create(db_session=session, group_in=group_in)
    assert group


def test_update(session, group):
    from dispatch.group.service import update
    from dispatch.group.models import GroupUpdate

    name = "Updated name"
    email = "updated@example.com"

    group_in = GroupUpdate(name=name, email=email)
    group = update(db_session=session, group=group, group_in=group_in)
    assert group.name == name
    assert group.email == email


def test_delete(session, group):
    from dispatch.group.service import delete, get

    delete(db_session=session, group_id=group.id)
    assert not get(db_session=session, group_id=group.id)
