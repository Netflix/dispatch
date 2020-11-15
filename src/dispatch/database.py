import re
import logging
import json
from typing import Any, List
from itertools import groupby
import functools

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Query, sessionmaker
from sqlalchemy_filters import apply_pagination, apply_sort, apply_filters
from sqlalchemy_searchable import make_searchable
from sqlalchemy_searchable import search as search_db
from starlette.requests import Request

from dispatch.common.utils.composite_search import CompositeSearch
from dispatch.enums import Visibility, UserRoles


from .config import SQLALCHEMY_DATABASE_URI

log = logging.getLogger(__file__)

engine = create_engine(str(SQLALCHEMY_DATABASE_URI))
SessionLocal = sessionmaker(bind=engine)


def resolve_table_name(name):
    """Resolves table names to their mapped names."""
    names = re.split("(?=[A-Z])", name)  # noqa
    return "_".join([x.lower() for x in names if x])


raise_attribute_error = object()


def resolve_attr(obj, attr, default=None):
    """Attempts to access attr via dotted notation, returns none if attr does not exist."""
    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except AttributeError:
        return default


class CustomBase:
    @declared_attr
    def __tablename__(self):
        return resolve_table_name(self.__name__)


Base = declarative_base(cls=CustomBase)

make_searchable(Base.metadata)


def get_db(request: Request):
    return request.state.db


def get_model_name_by_tablename(table_fullname: str) -> str:
    """Returns the model name of a given table."""
    return get_class_by_tablename(table_fullname=table_fullname).__name__


def get_class_by_tablename(table_fullname: str) -> Any:
    """Return class reference mapped to table."""
    mapped_name = resolve_table_name(table_fullname)
    for c in Base._decl_class_registry.values():
        if hasattr(c, "__table__"):
            if c.__table__.fullname.lower() == mapped_name.lower():
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


def create_filter_spec(model, fields, ops, values, user_role):
    """Creates a filter spec."""
    filters = []

    if fields and ops and values:
        for field, op, value in zip(fields, ops, values):
            if "." in field:
                complex_model, complex_field = field.split(".")
                filters.append(
                    {
                        "model": get_model_name_by_tablename(complex_model),
                        "field": complex_field,
                        "op": op,
                        "value": value,
                    }
                )
            else:
                filters.append({"model": model, "field": field, "op": op, "value": value})

    filter_spec = []
    # group by field (or for same fields and for different fields)
    data = sorted(filters, key=lambda x: x["model"])
    for k, g in groupby(data, key=lambda x: x["model"]):
        # force 'and' for operations other than equality
        filters = list(g)
        force_and = False
        for f in filters:
            if ">" in f["op"] or "<" in f["op"]:
                force_and = True

        if force_and:
            filter_spec.append({"and": filters})
        else:
            filter_spec.append({"or": filters})

    # add admin only filter
    if user_role != UserRoles.admin:
        # add support for filtering restricted incidents
        if model.lower() == "incident":
            filter_spec.append(
                {
                    "model": model,
                    "field": "visibility",
                    "op": "!=",
                    "value": Visibility.restricted,
                }
            )

    if filter_spec:
        filter_spec = {"and": filter_spec}

    log.debug(f"Filter Spec: {json.dumps(filter_spec, indent=2)}")
    return filter_spec


def create_sort_spec(model, sort_by, descending):
    """Creates sort_spec."""
    sort_spec = []
    if sort_by and descending:
        for field, direction in zip(sort_by, descending):
            direction = "desc" if direction else "asc"

            # we have a complex field, we may need to join
            if "." in field:
                complex_model, complex_field = field.split(".")[-2:]

                sort_spec.append(
                    {
                        "model": get_model_name_by_tablename(complex_model),
                        "field": complex_field,
                        "direction": direction,
                    }
                )
            else:
                sort_spec.append({"model": model, "field": field, "direction": direction})
    log.debug(f"Sort Spec: {json.dumps(sort_spec, indent=2)}")
    return sort_spec


def get_all(*, db_session, model):
    """Fetches a query object based on the model class name."""
    return db_session.query(get_class_by_tablename(model))


def join_required_attrs(query, model, join_attrs, fields, sort_by):
    """Determines which attrs (if any) require a join."""
    all_fields = list(set(fields + sort_by))

    if not join_attrs:
        return query

    for field, attr in join_attrs:
        # sometimes fields have attributes e.g. "incident_type.id"
        for f in all_fields:
            if field in f:
                query = query.join(getattr(model, attr))
    return query


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
    join_attrs: List[str] = None,
    user_role: UserRoles = UserRoles.user,
):
    """Common functionality for searching, filtering and sorting"""
    model_cls = get_class_by_tablename(model)
    if query_str:
        query = search(db_session=db_session, query_str=query_str, model=model)
    else:
        query = db_session.query(model_cls)

    query = join_required_attrs(query, model_cls, join_attrs, fields, sort_by)

    filter_spec = create_filter_spec(model, fields, ops, values, user_role)
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
