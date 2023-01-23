from typing import List, Optional

from sqlalchemy_filters import apply_filters

from dispatch.database.core import Base, get_class_by_tablename, get_table_name_by_class_instance
from dispatch.database.service import apply_filter_specific_joins
from dispatch.project import service as project_service

from .models import SearchFilter, SearchFilterCreate, SearchFilterUpdate


def get(*, db_session, search_filter_id: int) -> Optional[SearchFilter]:
    """Gets a search filter by id."""
    return db_session.query(SearchFilter).filter(SearchFilter.id == search_filter_id).first()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[SearchFilter]:
    """Gets a search filter by name."""
    return (
        db_session.query(SearchFilter)
        .filter(SearchFilter.name == name)
        .filter(SearchFilter.project_id == project_id)
        .first()
    )


def match(*, db_session, filter_spec: List[dict], class_instance: Base):
    """Matches a class instance with a given search filter."""
    table_name = get_table_name_by_class_instance(class_instance)
    model_cls = get_class_by_tablename(table_name)
    query = db_session.query(model_cls)

    query = apply_filter_specific_joins(model_cls, filter_spec, query)
    query = apply_filters(query, filter_spec)
    return query.filter(model_cls.id == class_instance.id).one_or_none()


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


def create(*, db_session, creator, search_filter_in: SearchFilterCreate) -> SearchFilter:
    """Creates a new search filter."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=search_filter_in.project
    )
    search_filter = SearchFilter(
        **search_filter_in.dict(exclude={"project"}), project=project, creator=creator
    )
    db_session.add(search_filter)
    db_session.commit()
    return search_filter


def update(
    *, db_session, search_filter: SearchFilter, search_filter_in: SearchFilterUpdate
) -> SearchFilter:
    """Updates a search filter."""
    search_filter_data = search_filter.dict()
    update_data = search_filter_in.dict(skip_defaults=True)

    for field in search_filter_data:
        if field in update_data:
            setattr(search_filter, field, update_data[field])

    db_session.commit()
    return search_filter


def delete(*, db_session, search_filter_id: int):
    """Deletes a search filter."""
    search_filter = (
        db_session.query(SearchFilter).filter(SearchFilter.id == search_filter_id).first()
    )
    db_session.delete(search_filter)
    db_session.commit()
