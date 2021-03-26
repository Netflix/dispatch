import logging
import json
from itertools import groupby

from typing import List

from sqlalchemy import and_, not_
from sqlalchemy.orm import Query
from sqlalchemy_filters import apply_pagination, apply_sort, apply_filters
from sqlalchemy_searchable import search as search_db

from dispatch.common.utils.composite_search import CompositeSearch
from dispatch.enums import Visibility, UserRoles
from dispatch.incident.models import Incident
from dispatch.individual.models import IndividualContact
from dispatch.participant.models import Participant

from .core import Base, get_class_by_tablename, get_model_name_by_tablename


log = logging.getLogger(__file__)


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


def search(*, db_session, query_str: str, model: str, sort=False):
    """Perform a search based on the query."""
    q = db_session.query(get_class_by_tablename(model))
    return search_db(q, query_str, sort=sort)


def create_filter_spec(model, fields, ops, values):
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
    filter_spec: List[dict] = None,
    page: int = 1,
    items_per_page: int = 5,
    sort_by: List[str] = None,
    descending: List[bool] = None,
    fields: List[str] = None,
    ops: List[str] = None,
    values: List[str] = None,
    join_attrs: List[str] = None,
    user_role: UserRoles = UserRoles.user.value,
    user_email: str = None,
):
    """Common functionality for searching, filtering, sorting, and pagination."""
    model_cls = get_class_by_tablename(model)
    sort_spec = create_sort_spec(model, sort_by, descending)

    if query_str:
        sort = False if sort_spec else True
        query = search(db_session=db_session, query_str=query_str, model=model, sort=sort)
    else:
        query = db_session.query(model_cls)

    if user_role != UserRoles.admin.value:
        if model.lower() == "incident":
            # we filter restricted incidents based on incident participation
            query = (
                query.join(Participant)
                .join(IndividualContact)
                .filter(
                    not_(
                        and_(
                            Incident.visibility == Visibility.restricted.value,
                            IndividualContact.email != user_email,
                        )
                    )
                )
            )

    query = join_required_attrs(query, model_cls, join_attrs, fields, sort_by)

    if not filter_spec:
        filter_spec = create_filter_spec(model, fields, ops, values)

    query = apply_filters(query, filter_spec)
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
