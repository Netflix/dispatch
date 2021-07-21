import pytest


def test_get_search_filter(session, search_filter):
    from dispatch.search_filter.service import get

    t_search_filter = get(db_session=session, search_filter_id=search_filter.id)
    assert t_search_filter.id == search_filter.id


def test_get_all(session, search_filters):
    from dispatch.search_filter.service import get_all

    t_search_filters = get_all(db_session=session).all()
    assert len(t_search_filters) > 1


def test_create(session, project):
    from dispatch.search_filter.service import create
    from dispatch.search_filter.models import SearchFilterCreate

    name = "name"
    description = "description"
    expression = [{}]
    type = "type"

    search_filter_in = SearchFilterCreate(
        name=name,
        description=description,
        expression=expression,
        type=type,
        project=project,
    )
    search_filter = create(db_session=session, search_filter_in=search_filter_in)
    assert search_filter


@pytest.mark.skip
def test_update(session, search_filter):
    from dispatch.search_filter.service import update
    from dispatch.search_filter.models import SearchFilterUpdate

    name = "Updated name"

    search_filter_in = SearchFilterUpdate(
        name=name,
    )
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
