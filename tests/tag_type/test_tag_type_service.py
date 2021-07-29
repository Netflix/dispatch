def test_get(session, tag_type):
    from dispatch.tag_type.service import get

    t_tag_type = get(db_session=session, tag_type_id=tag_type.id)
    assert t_tag_type.id == tag_type.id


def test_create(session, tag_type, project):
    from dispatch.tag_type.service import create
    from dispatch.tag_type.models import TagTypeCreate

    name = "name"
    description = "description"

    tag_type_in = TagTypeCreate(
        name=name,
        description=description,
        project=project,
    )
    tag_type = create(db_session=session, tag_type_in=tag_type_in)
    assert tag_type


def test_update(session, tag_type):
    from dispatch.tag_type.service import update
    from dispatch.tag_type.models import TagTypeUpdate

    name = "Updated name"

    tag_type_in = TagTypeUpdate(
        name=name,
    )
    tag_type = update(
        db_session=session,
        tag_type=tag_type,
        tag_type_in=tag_type_in,
    )
    assert tag_type.name == name


def test_delete(session, tag_type):
    from dispatch.tag_type.service import delete, get

    delete(db_session=session, tag_type_id=tag_type.id)
    assert not get(db_session=session, tag_type_id=tag_type.id)
