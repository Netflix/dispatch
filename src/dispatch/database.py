import re
from typing import Any, List

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Query, sessionmaker, scoped_session
from sqlalchemy_filters import apply_pagination, apply_sort, apply_filters
from sqlalchemy_searchable import make_searchable
from sqlalchemy_searchable import search as search_db
from starlette.requests import Request

from dispatch.common.utils.composite_search import CompositeSearch

from .config import SQLALCHEMY_DATABASE_URI

engine = create_engine(str(SQLALCHEMY_DATABASE_URI))
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


class CustomBase:
    @declared_attr
    def __tablename__(self):
        return resolve_table_name(self.__name__)


Base = declarative_base(cls=CustomBase)

make_searchable(Base.metadata)


def get_db(request: Request):
    return request.state.db


def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""
    mapped_name = resolve_table_name(table_fullname)
    for c in Base._decl_class_registry.values():
        if hasattr(c, "__table__") and c.__table__.fullname == mapped_name:
            return c
    raise Exception(f"Incorrect tablename '{mapped_name}'. Check the name of your model.")


def paginate(query: Query, page: int, items_per_page: int):
    # Never pass a negative OFFSET value to SQL.
    offset_adj = 0 if page <= 0 else page - 1
    items = query.limit(items_per_page).offset(offset_adj * items_per_page).all()
    total = query.order_by(None).count()
    return items, total


def composite_search(*, db_session, query_str: str, models: List[Base]):
    """Perform a multi-table search based on the supplied query."""
    s = CompositeSearch(db_session, models)
    q = s.build_query(query_str, sort=True)
    return s.search(query=q)


def search(*, db_session, query_str: str, model: str):
    """Perform a search based on the query."""
    q = db_session.query(get_class_by_tablename(model))
    return search_db(q, query_str, sort=True)


def create_filter_spec(model, fields, ops, values):
    """Creates a filter spec."""
    filter_spec = []
    if fields and ops and values:
        for field, op, value in zip(fields, ops, values):
            filter_spec.append({"model": model, "field": field, "op": op, "value": value})
    return filter_spec


def create_sort_spec(model, sort_by, descending):
    """Creates sort_spec."""
    sort_spec = []
    if sort_by and descending:
        for field, direction in zip(sort_by, descending):
            direction = "desc" if direction else "asc"
            sort_spec.append({"model": model, "field": field, "direction": direction})
    return sort_spec


def get_all(*, db_session, model):
    """Fetches a query object based on the model class name."""
    return db_session.query(get_class_by_tablename(model))


def search_filter_sort_paginate(
    db_session,
    model,
    query_str: str = None,
    page: int = 1,
    items_per_page: int = 5,
    sort_by: List[str] = None,
    descending: List[bool] = None,
    fields: List[str] = None,
    ops: List[str] = None,
    values: List[str] = None,
):
    """Common functionality for searching, filtering and sorting"""
    if query_str:
        query = search(db_session=db_session, query_str=query_str, model=model)
    else:
        query = get_all(db_session=db_session, model=model)

    filter_spec = create_filter_spec(model, fields, ops, values)
    query = apply_filters(query, filter_spec)

    sort_spec = create_sort_spec(model, sort_by, descending)
    query = apply_sort(query, sort_spec)

    if items_per_page == -1:
        items_per_page = None

    query, pagination = apply_pagination(query, page_number=page, page_size=items_per_page)

    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,
    }
