def test_get(session, tag):
    from dispatch.tag.service import get

    t_tag = get(db_session=session, tag_id=tag.id)
    assert t_tag.id == tag.id


def test_create(session, tag_type, project):
    from dispatch.tag.service import create
    from dispatch.tag.models import TagCreate

    name = "name"
    description = "description"
    uri = "https://www.example.com/"
    source = "dispatch"
    discoverable = True

    tag_in = TagCreate(
        name=name,
        description=description,
        uri=uri,
        source=source,
        discoverable=discoverable,
        tag_type=tag_type,
        project=project,
    )
    tag = create(db_session=session, tag_in=tag_in)
    assert tag


def test_update(session, tag):
    from dispatch.tag.service import update
    from dispatch.tag.models import TagUpdate

    name = "updated name"

    tag_in = TagUpdate(
        name=name,
    )
    tag = update(
        db_session=session,
        tag=tag,
        tag_in=tag_in,
    )
    assert tag.name == name


def test_delete(session, tag):
    from dispatch.tag.service import delete, get

    delete(db_session=session, tag_id=tag.id)
    assert not get(db_session=session, tag_id=tag.id)
