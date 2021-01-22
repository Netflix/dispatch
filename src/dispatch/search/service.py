from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy_searchable import search as search_db
from sqlalchemy_filters import apply_filters

from dispatch.database import Base, get_class_by_tablename
from dispatch.common.utils.composite_search import CompositeSearch
from .models import SearchFilter, SearchFilterCreate, SearchFilterUpdate


def get(*, db_session, search_filter_id: int) -> Optional[SearchFilter]:
    """Gets a search filter by id."""
    return db_session.query(SearchFilter).filter(SearchFilter.id == search_filter_id).first()


def get_by_name(*, db_session, name: str) -> Optional[SearchFilter]:
    """Gets a search filter by name."""
    return db_session.query(SearchFilter).filter(SearchFilter.name == name).first()


def match(*, db_session, filter_spec, model, model_id: int):
    """Matches an incident with a given search filter."""
    model_cls = get_class_by_tablename(model)
    query = db_session.query(model_cls)
    query = apply_filters(query, filter_spec)
    return query.filter(model.id == model_id).one_or_none()


def get_or_create(*, db_session, search_filter_in) -> SearchFilter:
    if search_filter_in.id:
        q = db_session.query(SearchFilter).filter(SearchFilter.id == search_filter_in.id)
    else:
        q = db_session.query(SearchFilter).filter_by(**search_filter_in.dict(exclude={"id"}))

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, search_filter_in=search_filter_in)


def get_all(*, db_session):
    """Gets all search filters."""
    return db_session.query(SearchFilter)


def create(*, db_session, search_filter_in: SearchFilterCreate) -> SearchFilter:
    """Creates a new search filter."""
    search_filter = SearchFilter(**search_filter_in.dict())
    db_session.add(search_filter)
    db_session.commit()
    return search_filter


def update(
    *, db_session, search_filter: SearchFilter, search_filter_in: SearchFilterUpdate
) -> SearchFilter:
    """Updates a search filter."""
    search_filter_data = jsonable_encoder(search_filter)
    update_data = search_filter_in.dict(skip_defaults=True)

    for field in search_filter_data:
        if field in update_data:
            setattr(search_filter, field, update_data[field])

    db_session.add(search_filter)
    db_session.commit()
    return search_filter


def create_or_update(*, db_session, search_filter_in: SearchFilterCreate) -> SearchFilter:
    """Creates or updates a search filter."""
    update_data = search_filter_in.dict(skip_defaults=True)

    q = db_session.query(SearchFilter)
    for attr, value in update_data.items():
        q = q.filter(getattr(SearchFilter, attr) == value)

    instance = q.first()

    if instance:
        return update(
            db_session=db_session, search_filter=instance, search_filter_in=search_filter_in
        )

    return create(db_session=db_session, search_filter_in=search_filter_in)


def delete(*, db_session, search_filter_id: int):
    """Delets a search filter."""
    search_filter = (
        db_session.query(SearchFilter).filter(SearchFilter.id == search_filter_id).first()
    )
    db_session.delete(search_filter)
    db_session.commit()


def composite_search(*, db_session, query_str: str, models: List[Base]):
    """Perform a multi-table search based on the supplied query."""
    s = CompositeSearch(db_session, models)
    q = s.build_query(query_str, sort=True)
    return s.search(query=q)


def search(*, db_session, query_str: str, model: Base):
    """Perform a search based on the query."""
    q = db_session.query(model)
    return search_db(q, query_str, sort=True)
