def test_get(session, search_filter):
    from dispatch.search_filter.service import get

    t_search_filter = get(db_session=session, search_filter_id=search_filter.id)
    assert t_search_filter.id == search_filter.id


def test_create(session, user, project):
    from dispatch.search_filter.service import create
    from dispatch.search_filter.models import SearchFilterCreate

    name = "name"
    description = "description"
    expression = [{}]

    search_filter_in = SearchFilterCreate(
        name=name,
        description=description,
        expression=expression,
        project=project,
    )
    search_filter = create(db_session=session, creator=user, search_filter_in=search_filter_in)
    assert search_filter


def test_update(session, search_filter):
    from dispatch.search_filter.service import update
    from dispatch.search_filter.models import SearchFilterUpdate

    name = "Updated name"

    search_filter_in = SearchFilterUpdate(name=name, expression=[{}])
    search_filter = update(
        db_session=session,
        search_filter=search_filter,
        search_filter_in=search_filter_in,
    )
    assert search_filter.name == name


def test_delete(session, search_filter):
    from dispatch.search_filter.service import delete, get

    delete(db_session=session, search_filter_id=search_filter.id)
    assert not get(db_session=session, search_filter_id=search_filter.id)
