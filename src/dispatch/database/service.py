import logging
import json

from typing import List

from fastapi import Depends, Query

from sqlalchemy import or_, orm, func, desc
from sqlalchemy_filters import apply_pagination, apply_sort, apply_filters


from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user
from dispatch.search.fulltext.composite_search import CompositeSearch
from dispatch.enums import Visibility
from dispatch.feedback.models import Feedback
from dispatch.task.models import Task
from dispatch.project.models import Project
from dispatch.plugin.models import Plugin, PluginInstance
from dispatch.incident.models import Incident
from dispatch.incident_type.models import IncidentType
from dispatch.individual.models import IndividualContact
from dispatch.participant.models import Participant


from .core import (
    Base,
    get_class_by_tablename,
    get_model_name_by_tablename,
    get_db,
)


log = logging.getLogger(__file__)


def restricted_incident_filter(query: orm.Query, current_user: DispatchUser):
    """Adds additional incident filters to query (usually for permissions)."""
    query = (
        query.join(Participant, Incident.id == Participant.incident_id)
        .join(IndividualContact)
        .filter(
            or_(
                Incident.visibility == Visibility.open.value,
                IndividualContact.email == current_user.email,
            )
        )
        .distinct()
    )
    return query


def restricted_incident_type_filter(query: orm.Query, current_user: DispatchUser):
    """Adds additional incident type filters to query (usually for permissions)."""
    if current_user:
        query = query.filter(IncidentType.visibility == Visibility.open.value)
    return query


def apply_model_specific_filters(model: Base, query: orm.Query, current_user: DispatchUser):
    """Applies any model specific filter as it pertains to the given user."""
    model_map = {
        Incident: [restricted_incident_filter],
        # IncidentType: [restricted_incident_type_filter],
    }

    filters = model_map.get(model, [])

    for f in filters:
        query = f(query, current_user)

    return query


def apply_model_specific_joins(model: Base, query: orm.query):
    """Applies any model specific implicity joins."""
    model_map = {
        Feedback: [(Incident, False), (Project, False)],
        Task: [(Incident, False), (Project, False)],
        PluginInstance: [(Plugin, False)],
        Incident: [(Incident.tags, True), (Incident.terms, True)],
    }

    joined_models = model_map.get(model, [])

    for model, is_outer in joined_models:
        query = query.join(model, isouter=is_outer)

    return query


def paginate(query: orm.Query, page: int, items_per_page: int):
    # Never pass a negative OFFSET value to SQL.
    offset_adj = 0 if page <= 0 else page - 1
    items = query.limit(items_per_page).offset(offset_adj * items_per_page).all()
    total = query.order_by(None).count()
    return items, total


def composite_search(*, db_session, query_str: str, models: List[Base], current_user: DispatchUser):
    """Perform a multi-table search based on the supplied query."""
    s = CompositeSearch(db_session, models)
    query = s.build_query(query_str, sort=True)

    # TODO can we do this with composite filtering?
    # for model in models:
    #    query = apply_model_specific_filters(model, query, current_user)

    return s.search(query=query)


def search(*, query_str: str, query: Query, model: str, sort=False):
    """Perform a search based on the query."""
    search_model = get_class_by_tablename(model)

    if not query_str.strip():
        return query

    vector = search_model.search_vector

    query = query.filter(vector.op("@@")(func.tsq_parse(query_str)))
    if sort:
        query = query.order_by(desc(func.ts_rank_cd(vector, func.tsq_parse(query_str))))

    return query.params(term=query_str)


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


def common_parameters(
    db_session: orm.Session = Depends(get_db),
    page: int = 1,
    items_per_page: int = Query(5, alias="itemsPerPage"),
    query_str: str = Query(None, alias="q"),
    filter_spec: str = Query([], alias="filter"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    current_user: DispatchUser = Depends(get_current_user),
):
    if filter_spec:
        filter_spec = json.loads(filter_spec)

    return {
        "db_session": db_session,
        "page": page,
        "items_per_page": items_per_page,
        "query_str": query_str,
        "filter_spec": filter_spec,
        "sort_by": sort_by,
        "descending": descending,
        "current_user": current_user,
    }


def search_filter_sort_paginate(
    db_session,
    model,
    query_str: str = None,
    filter_spec: List[dict] = None,
    page: int = 1,
    items_per_page: int = 5,
    sort_by: List[str] = None,
    descending: List[bool] = None,
    current_user: DispatchUser = None,
):
    """Common functionality for searching, filtering, sorting, and pagination."""
    model_cls = get_class_by_tablename(model)
    sort_spec = create_sort_spec(model, sort_by, descending)

    query = db_session.query(model_cls)
    query = apply_model_specific_joins(model_cls, query)

    if query_str:
        sort = False if sort_by else True
        query = search(query_str=query_str, query=query, model=model, sort=sort)

    query = apply_model_specific_filters(model_cls, query, current_user)

    if filter_spec:
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
