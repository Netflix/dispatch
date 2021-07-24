import logging
import json

from typing import List
from pydantic.types import Json, constr

from fastapi import Depends, Query

from sqlalchemy import or_, orm, func, desc
from sqlalchemy_filters import apply_pagination, apply_sort, apply_filters
from sqlalchemy_filters.filters import build_filters, get_named_models
from sqlalchemy_filters.models import get_query_models


from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user, get_current_role
from dispatch.enums import UserRoles, Visibility
from dispatch.incident.models import Incident
from dispatch.feedback.models import Feedback
from dispatch.task.models import Task
from dispatch.plugin.models import Plugin, PluginInstance
from dispatch.incident_type.models import IncidentType
from dispatch.individual.models import IndividualContact
from dispatch.participant.models import Participant
from dispatch.search.fulltext.composite_search import CompositeSearch


from .core import (
    Base,
    get_class_by_tablename,
    get_model_name_by_tablename,
    get_db,
)


log = logging.getLogger(__file__)


def restricted_incident_filter(query: orm.Query, current_user: DispatchUser, role: UserRoles):
    """Adds additional incident filters to query (usually for permissions)."""
    if role != UserRoles.owner:
        # We don't allow users that are not owners to see restricted incidents
        query = (
            query.join(Participant, Incident.id == Participant.incident_id)
            .join(IndividualContact)
            .filter(
                or_(
                    Incident.visibility == Visibility.open,
                    IndividualContact.email == current_user.email,
                )
            )
        )
    return query.distinct()


def restricted_incident_type_filter(query: orm.Query, current_user: DispatchUser):
    """Adds additional incident type filters to query (usually for permissions)."""
    if current_user:
        query = query.filter(IncidentType.visibility == Visibility.open)
    return query


def apply_model_specific_filters(
    model: Base, query: orm.Query, current_user: DispatchUser, role: UserRoles
):
    """Applies any model specific filter as it pertains to the given user."""
    model_map = {
        Incident: [restricted_incident_filter],
        # IncidentType: [restricted_incident_type_filter],
    }

    filters = model_map.get(model, [])

    for f in filters:
        query = f(query, current_user, role)

    return query


def apply_filter_specific_joins(model: Base, filter_spec: dict, query: orm.query):
    """Applies any model specific implicity joins."""
    # this is required because by default sqlalchemy-filter's auto-join
    # knows nothing about how to join many-many relationships.
    model_map = {
        (Feedback, "Project"): (Incident, False),
        (Feedback, "Incident"): (Incident, False),
        (Task, "Project"): (Incident, False),
        (Task, "Incident"): (Incident, False),
        (Task, "IncidentPriority"): (Incident, False),
        (Task, "IncidentType"): (Incident, False),
        (PluginInstance, "Plugin"): (Plugin, False),
        (DispatchUser, "Organization"): (DispatchUser.organizations, True),
        (Incident, "Tag"): (Incident.tags, True),
        (Incident, "TagType"): (Incident.tags, True),
        (Incident, "Terms"): (Incident.terms, True),
    }
    filters = build_filters(filter_spec)
    filter_models = get_named_models(filters)

    for filter_model in filter_models:
        if model_map.get((model, filter_model)):
            joined_model, is_outer = model_map[(model, filter_model)]
            if joined_model not in get_query_models(query).values():
                query = query.join(joined_model, isouter=is_outer)

    return query


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
    page: int = Query(1, gt=0, lt=9223372036854775807),
    items_per_page: int = Query(5, alias="itemsPerPage", gt=0, lt=9223372036854775807),
    query_str: constr(strip_whitespace=True, min_length=1) = Query(None, alias="q"),
    filter_spec: Json = Query([], alias="filter"),
    sort_by: List[str] = Query([], alias="sortBy[]"),
    descending: List[bool] = Query([], alias="descending[]"),
    current_user: DispatchUser = Depends(get_current_user),
    role: UserRoles = Depends(get_current_role),
):
    return {
        "db_session": db_session,
        "page": page,
        "items_per_page": items_per_page,
        "query_str": query_str,
        "filter_spec": filter_spec,
        "sort_by": sort_by,
        "descending": descending,
        "current_user": current_user,
        "role": role,
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
    role: UserRoles = UserRoles.member,
):
    """Common functionality for searching, filtering, sorting, and pagination."""
    model_cls = get_class_by_tablename(model)
    sort_spec = create_sort_spec(model, sort_by, descending)

    query = db_session.query(model_cls)

    if query_str:
        sort = False if sort_by else True
        query = search(query_str=query_str, query=query, model=model, sort=sort)

    query = apply_model_specific_filters(model_cls, query, current_user, role)

    if filter_spec:
        query = apply_filter_specific_joins(model_cls, filter_spec, query)
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
