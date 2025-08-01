import logging
import json
from collections import namedtuple
from collections.abc import Iterable
from inspect import signature
from itertools import chain

from fastapi import Depends, Query
from pydantic import StringConstraints
from pydantic import Json
from six import string_types
from sortedcontainers import SortedSet
from sqlalchemy import Table, and_, desc, func, not_, or_, orm
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from sqlalchemy.orm import mapperlib, Query as SQLAlchemyQuery
from sqlalchemy_filters import apply_pagination, apply_sort
from sqlalchemy_filters.exceptions import BadFilterFormat, FieldNotFound
from sqlalchemy_filters.models import Field, BadQuery, BadSpec

from .core import Base, get_class_by_tablename, get_model_name_by_tablename
from dispatch.auth.models import DispatchUser
from dispatch.auth.service import CurrentUser, get_current_role
from dispatch.case.models import Case
from dispatch.data.query.models import Query as QueryModel
from dispatch.data.source.models import Source
from dispatch.database.core import DbSession
from dispatch.enums import UserRoles, Visibility
from dispatch.feedback.incident.models import Feedback
from dispatch.incident.models import Incident
from dispatch.incident.type.models import IncidentType
from dispatch.individual.models import IndividualContact
from dispatch.participant.models import Participant
from dispatch.plugin.models import Plugin, PluginInstance
from dispatch.project.models import Project
from dispatch.search.fulltext.composite_search import CompositeSearch
from dispatch.signal.models import Signal, SignalInstance
from dispatch.tag.models import Tag

from dispatch.task.models import Task
from typing import Annotated

log = logging.getLogger(__file__)

# allows only printable characters
QueryStr = Annotated[str, StringConstraints(pattern=r"^[ -~]+$", min_length=1)]

BooleanFunction = namedtuple("BooleanFunction", ("key", "sqlalchemy_fn", "only_one_arg"))
BOOLEAN_FUNCTIONS = [
    BooleanFunction("or", or_, False),
    BooleanFunction("and", and_, False),
    BooleanFunction("not", not_, True),
]


class Operator(object):
    OPERATORS = {
        "is_null": lambda f: f.is_(None),
        "is_not_null": lambda f: f.isnot(None),
        "==": lambda f, a: f == a,
        "eq": lambda f, a: f == a,
        "!=": lambda f, a: f != a,
        "ne": lambda f, a: f != a,
        ">": lambda f, a: f > a,
        "gt": lambda f, a: f > a,
        "<": lambda f, a: f < a,
        "lt": lambda f, a: f < a,
        ">=": lambda f, a: f >= a,
        "ge": lambda f, a: f >= a,
        "<=": lambda f, a: f <= a,
        "le": lambda f, a: f <= a,
        "like": lambda f, a: f.like(a),
        "ilike": lambda f, a: f.ilike(a),
        "not_ilike": lambda f, a: ~f.ilike(a),
        "in": lambda f, a: f.in_(a),
        "not_in": lambda f, a: ~f.in_(a),
        "any": lambda f, a: f.any(a),
        "not_any": lambda f, a: func.not_(f.any(a)),
    }

    def __init__(self, operator=None):
        if not operator:
            operator = "=="

        if operator not in self.OPERATORS:
            raise BadFilterFormat("Operator `{}` not valid.".format(operator))

        self.operator = operator
        self.function = self.OPERATORS[operator]
        self.arity = len(signature(self.function).parameters)


class Filter(object):
    def __init__(self, filter_spec):
        self.filter_spec = filter_spec

        try:
            filter_spec["field"]
        except KeyError:
            raise BadFilterFormat("`field` is a mandatory filter attribute.") from None
        except TypeError:
            raise BadFilterFormat(
                "Filter spec `{}` should be a dictionary.".format(filter_spec)
            ) from None

        self.operator = Operator(filter_spec.get("op"))
        self.value = filter_spec.get("value")
        value_present = True if "value" in filter_spec else False
        if not value_present and self.operator.arity == 2:
            raise BadFilterFormat("`value` must be provided.")

    def get_named_models(self):
        if "model" in self.filter_spec:
            model = self.filter_spec["model"]
            if model in ["Participant", "Commander", "Assignee"]:
                return {"IndividualContact"}
            if model == "TagAll":
                return {"Tag"}
            if model == "NotCaseType":
                return {"CaseType"}
            else:
                return {self.filter_spec["model"]}
        return set()

    def format_for_sqlalchemy(self, query: SQLAlchemyQuery, default_model):
        filter_spec = self.filter_spec
        if filter_spec.get("model") in ["Participant", "Commander", "Assignee"]:
            filter_spec["model"] = "IndividualContact"
        elif filter_spec.get("model") == "NotCaseType":
            filter_spec["model"] = "CaseType"
        elif filter_spec.get("model") == "TagAll":
            filter_spec["model"] = "Tag"

        operator = self.operator
        value = self.value

        # Special handling for TagType.id filtering on Tag model
        # Needed since TagType.id is not a column on the Tag model
        # Convert TagType.id filter to tag_type_id filter on Tag model
        if (
            filter_spec.get("model") == "TagType"
            and filter_spec.get("field") == "id"
            and default_model
            and getattr(default_model, "__tablename__", None) == "tag"
        ):
            filter_spec = {"model": "Tag", "field": "tag_type_id", "op": filter_spec.get("op")}

        model = get_model_from_spec(filter_spec, query, default_model)

        function = operator.function
        arity = operator.arity

        field_name = filter_spec["field"]
        field = Field(model, field_name)
        sqlalchemy_field = field.get_sqlalchemy_field()

        if arity == 1:
            return function(sqlalchemy_field)

        if arity == 2:
            return function(sqlalchemy_field, value)


def get_model_from_spec(spec, query, default_model=None):
    """Determine the model to which a spec applies on a given query.
    A spec that does not specify a model may be applied to a query that
    contains a single model. Otherwise the spec must specify the model to
    which it applies, and that model must be present in the query.
    :param query:
        A :class:`sqlalchemy.orm.Query` instance.
    :param spec:
        A dictionary that may or may not contain a model name to resolve
        against the query.
    :returns:
        A model instance.
    :raise BadSpec:
        If the spec is ambiguous or refers to a model not in the query.
    :raise BadQuery:
        If the query contains no models.
    """
    models = get_query_models(query)
    if not models:
        raise BadQuery("The query does not contain any models.")

    model_name = spec.get("model")
    if model_name is not None:
        models = [v for (k, v) in models.items() if k == model_name]
        if not models:
            raise BadSpec(f"The query had models {models} does not contain model `{model_name}`.")
        model = models[0]
    else:
        if len(models) == 1:
            model = list(models.values())[0]
        elif default_model is not None:
            return default_model
        else:
            raise BadSpec("Ambiguous spec. Please specify a model.")

    return model


class BooleanFilter(object):
    def __init__(self, function, *filters):
        self.function = function
        self.filters = filters

    def get_named_models(self):
        models = SortedSet()
        for filter in self.filters:
            named_models = filter.get_named_models()
            if named_models:
                models.add(*named_models)
        return models

    def format_for_sqlalchemy(self, query: SQLAlchemyQuery, default_model):
        return self.function(
            *[filter.format_for_sqlalchemy(query, default_model) for filter in self.filters]
        )


def _is_iterable_filter(filter_spec):
    """`filter_spec` may be a list of nested filter specs, or a dict."""
    return isinstance(filter_spec, Iterable) and not isinstance(filter_spec, (string_types, dict))


def build_filters(filter_spec):
    """Recursively process `filter_spec`"""
    if _is_iterable_filter(filter_spec):
        return list(chain.from_iterable(build_filters(item) for item in filter_spec))

    if isinstance(filter_spec, dict):
        # Check if filter spec defines a boolean function.
        for boolean_function in BOOLEAN_FUNCTIONS:
            if boolean_function.key in filter_spec:
                # The filter spec is for a boolean-function
                # Get the function argument definitions and validate
                fn_args = filter_spec[boolean_function.key]

                if not _is_iterable_filter(fn_args):
                    raise BadFilterFormat(
                        "`{}` value must be an iterable across the function arguments".format(
                            boolean_function.key
                        )
                    )
                if boolean_function.only_one_arg and len(fn_args) != 1:
                    raise BadFilterFormat(
                        "`{}` must have one argument".format(boolean_function.key)
                    )
                if not boolean_function.only_one_arg and len(fn_args) < 1:
                    raise BadFilterFormat(
                        "`{}` must have one or more arguments".format(boolean_function.key)
                    )
                return [BooleanFilter(boolean_function.sqlalchemy_fn, *build_filters(fn_args))]

    return [Filter(filter_spec)]


def get_model_from_table(table: Table):  # pragma: nocover
    """Resolve model class from table object"""

    for registry in mapperlib._all_registries():
        for mapper in registry.mappers:
            if table in mapper.tables:
                return mapper.class_
    return None


def get_query_models(query):
    """Get models from query.

    :param query:
        A :class:`sqlalchemy.orm.Query` instance.

    :returns:
        A dictionary with all the models included in the query.
    """
    models = [col_desc["entity"] for col_desc in query.column_descriptions]

    # In SQLAlchemy 2.x, we need to use a different approach to get joined entities
    try:
        # Try to get the statement from the query
        stmt = query.statement

        # Extract entities from the statement's froms
        for from_obj in stmt.froms:
            if hasattr(from_obj, "entity"):
                # For select statements with an entity
                if from_obj.entity not in models:
                    models.append(from_obj.entity)
            elif hasattr(from_obj, "left") and hasattr(from_obj, "right"):
                # For join objects
                for side in [from_obj.left, from_obj.right]:
                    if hasattr(side, "entity"):
                        if side.entity not in models:
                            models.append(side.entity)
                    elif hasattr(side, "table"):
                        model_class = get_model_from_table(side.table)
                        if model_class and model_class not in models:
                            models.append(model_class)

        # Try to extract joined entities from the query's _join_entities
        # This is for SQLAlchemy 2.x's internal structure
        if hasattr(query, "_compile_state"):
            try:
                compile_state = query._compile_state()
                if hasattr(compile_state, "_join_entities"):
                    for mapper in compile_state._join_entities:
                        if hasattr(mapper, "class_"):
                            if mapper.class_ not in models:
                                models.append(mapper.class_)
            except Exception:
                pass
    except (AttributeError, InvalidRequestError):
        # If we can't get the statement or process it, fall back to simpler approach
        pass

    return {model.__name__: model for model in models}


def get_model_class_by_name(registry, name):
    """Return the model class matching `name` in the given `registry`."""
    for cls in registry.values():
        if getattr(cls, "__name__", None) == name:
            return cls


def get_named_models(filters):
    models = []
    for filter in filters:
        models.extend(filter.get_named_models())
    return models


def get_default_model(query):
    """Return the singular model from `query`, or `None` if `query` contains
    multiple models.
    """
    query_models = get_query_models(query).values()
    if len(query_models) == 1:
        (default_model,) = iter(query_models)
    else:
        default_model = None
    return default_model


def auto_join(query, *model_names):
    """Automatically join models to `query` if they're not already present
    and the join can be done implicitly.
    """
    # every model has access to the registry, so we can use any from the query
    query_models = get_query_models(query).values()
    last_model = list(query_models)[-1]
    model_registry = last_model.registry._class_registry

    for name in model_names:
        model = get_model_class_by_name(model_registry, name)
        if model and (model not in get_query_models(query).values()):
            try:  # pragma: nocover
                # https://docs.sqlalchemy.org/en/14/changelog/migration_14.html
                # Many Core and ORM statement objects now perform much of
                # their construction and validation in the compile phase
                tmp = query.join(model)
                tmp._compile_state()
                query = tmp
            except InvalidRequestError:
                pass  # can't be autojoined
    return query


def apply_model_specific_filters(
    model: Base, query: orm.Query, current_user: DispatchUser, role: UserRoles
):
    """Applies any model specific filter as it pertains to the given user."""
    model_map = {
        Incident: [restricted_incident_filter],
        Case: [restricted_case_filter],
        # IncidentType: [restricted_incident_type_filter],
    }

    filters = model_map.get(model, [])

    for f in filters:
        query = f(query, current_user, role)

    return query


def apply_filters(query, filter_spec, model_cls=None, do_auto_join=True):
    """Apply filters to a SQLAlchemy query.

    :param query:
                    A :class:`sqlalchemy.orm.Query` instance.

    :param filter_spec:
                    A dict or an iterable of dicts, where each one includes
                    the necessary information to create a filter to be applied to the
                    query.

                    Example::

                                    filter_spec = [
                                                    {'model': 'Foo', 'field': 'name', 'op': '==', 'value': 'foo'},
                                    ]

                    If the query being modified refers to a single model, the `model` key
                    may be omitted from the filter spec.

                    Filters may be combined using boolean functions.

                    Example:

                                    filter_spec = {
                                                    'or': [
                                                                    {
                                                                        'model': 'Foo',
                                                                        'field': 'id',
                                                                        'op': '==',
                                                                        'value': '1'
                                                                    },
                                                                    {
                                                                        'model': 'Bar',
                                                                        'field': 'id',
                                                                        'op': '==',
                                                                        'value': '2'
                                                                    },
                                                    ]
                                    }

    :returns:
                    The :class:`sqlalchemy.orm.Query` instance after all the filters
                    have been applied.
    """
    default_model = get_default_model(query)
    if not default_model:
        default_model = model_cls

    filters = build_filters(filter_spec)
    filter_models = get_named_models(filters)

    if do_auto_join:
        query = auto_join(query, *filter_models)

    sqlalchemy_filters = [filter.format_for_sqlalchemy(query, default_model) for filter in filters]

    if sqlalchemy_filters:
        query = query.filter(*sqlalchemy_filters)

    return query


def apply_filter_specific_joins(model: Base, filter_spec: dict, query: orm.query):
    """Applies any model specific implicitly joins."""
    # this is required because by default sqlalchemy-filter's auto-join
    # knows nothing about how to join many-many relationships.
    model_map = {
        (Feedback, "Incident"): (Incident, False),
        (Feedback, "Case"): (Case, False),
        (Task, "Project"): (Incident, False),
        (Task, "Incident"): (Incident, False),
        (Task, "IncidentPriority"): (Incident, False),
        (Task, "IncidentType"): (Incident, False),
        (PluginInstance, "Plugin"): (Plugin, False),
        (Source, "Tag"): (Source.tags, True),
        (Source, "TagType"): (Source.tags, True),
        (QueryModel, "Tag"): (QueryModel.tags, True),
        (QueryModel, "TagType"): (QueryModel.tags, True),
        (DispatchUser, "Organization"): (DispatchUser.organizations, True),
        (Case, "Tag"): (Case.tags, True),
        (Case, "TagType"): (Case.tags, True),
        (Case, "IndividualContact"): (Case.participants, True),
        (Incident, "Tag"): (Incident.tags, True),
        (Incident, "TagType"): (Incident.tags, True),
        (Incident, "IndividualContact"): (Incident.participants, True),
        (Incident, "Term"): (Incident.terms, True),
        (Signal, "Tag"): (Signal.tags, True),
        (Signal, "TagType"): (Signal.tags, True),
        (SignalInstance, "Entity"): (SignalInstance.entities, True),
        (SignalInstance, "EntityType"): (SignalInstance.entities, True),
        # (Tag, "TagType"): (TagType, False),  # Disabled: filtering by tag_type_id directly
        (Tag, "Project"): (Project, False),
        (IndividualContact, "Project"): (Project, False),
    }
    filters = build_filters(filter_spec)

    # Replace mapping if looking for commander
    if "Commander" in str(filter_spec):
        model_map.update({(Incident, "IndividualContact"): (Incident.commander, True)})
    if "Assignee" in str(filter_spec):
        model_map.update({(Case, "IndividualContact"): (Case.assignee, True)})

    filter_models = get_named_models(filters)
    joined_models = []
    for filter_model in filter_models:
        if model_map.get((model, filter_model)):
            joined_model, is_outer = model_map[(model, filter_model)]
            try:
                # Use the model or table itself for tracking joins
                model_or_table = getattr(joined_model, "parent", joined_model)
                if model_or_table not in joined_models:
                    query = query.join(joined_model, isouter=is_outer)
                    joined_models.append(model_or_table)
            except Exception as e:
                log.exception(e)

    return query


def composite_search(*, db_session, query_str: str, models: list[Base], current_user: DispatchUser):
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

    search = []
    if hasattr(search_model, "search_vector"):
        vector = search_model.search_vector
        search.append(vector.op("@@")(func.tsq_parse(query_str)))

    if hasattr(search_model, "name"):
        search.append(
            search_model.name.ilike(f"%{query_str}%"),
        )
        search.append(search_model.name == query_str)

    if not search:
        raise Exception(f"Search not supported for model: {model}")

    query = query.filter(or_(*search))

    if sort:
        query = query.order_by(desc(func.ts_rank_cd(vector, func.tsq_parse(query_str))))

    return query.params(term=query_str)


def create_sort_spec(model, sort_by, descending):
    """Creates sort_spec."""
    sort_spec = []
    if sort_by and descending:
        for field, direction in zip(sort_by, descending, strict=False):
            direction = "desc" if direction else "asc"

            # check to see if field is json with a key parameter
            try:
                new_field = json.loads(field)
                field = new_field.get("key", "")
            except json.JSONDecodeError:
                pass

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
    current_user: CurrentUser,
    db_session: DbSession,
    page: int = Query(1, gt=0, lt=2147483647),
    items_per_page: int = Query(5, alias="itemsPerPage", gt=-2, lt=2147483647),
    query_str: QueryStr = Query(None, alias="q"),
    filter_spec: QueryStr = Query(None, alias="filter"),
    sort_by: list[str] = Query([], alias="sortBy[]"),
    descending: list[bool] = Query([], alias="descending[]"),
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


CommonParameters = Annotated[
    dict[str, int | CurrentUser | DbSession | QueryStr | Json | list[str] | list[bool] | UserRoles],
    Depends(common_parameters),
]


def has_filter_model(model: str, filter_spec: list[dict]):
    """Checks if the filter spec has a TagAll filter."""

    if isinstance(filter_spec, list):
        return False

    for key, value in filter_spec.items():
        if key == "and":
            for condition in value:
                or_condition = condition.get("or", [])
                if or_condition and or_condition[0].get("model") == model:
                    return True
    return False


def has_tag_all(filter_spec: list[dict]):
    return has_filter_model("TagAll", filter_spec)


def has_not_case_type(filter_spec: list[dict]):
    return has_filter_model("NotCaseType", filter_spec)


def rebuild_filter_spec_for_not_case_type(filter_spec: dict):
    new_filter_spec = []
    for key, value in filter_spec.items():
        if key == "and":
            for condition in value:
                or_condition = condition.get("or", [])
                if or_condition and or_condition[0].get("model") == "NotCaseType":
                    for cond in or_condition:
                        cond["op"] = "!="
                        new_filter_spec.append({"and": [{"and": [cond]}]})
                else:
                    new_filter_spec.append(condition)
    return {"and": new_filter_spec}


def rebuild_filter_spec_without_tag_all(filter_spec: dict):
    """Rebuilds the filter spec without the TagAll filter."""
    new_filter_spec = []
    tag_all_spec = []
    for key, value in filter_spec.items():
        if key == "and":
            for condition in value:
                or_condition = condition.get("or", [])
                if or_condition and or_condition[0].get("model") == "TagAll":
                    for cond in or_condition:
                        tag_all_spec.append({"and": [{"or": [cond]}]})
                else:
                    new_filter_spec.append(condition)
    return ({"and": new_filter_spec} if len(new_filter_spec) else None, tag_all_spec)


def search_filter_sort_paginate(
    db_session,
    model,
    query_str: str = None,
    filter_spec: str | dict | None = None,
    page: int = 1,
    items_per_page: int = 5,
    sort_by: list[str] = None,
    descending: list[bool] = None,
    current_user: DispatchUser = None,
    role: UserRoles = UserRoles.member,
):
    """Common functionality for searching, filtering, sorting, and pagination."""
    model_cls = get_class_by_tablename(model)

    try:
        query = db_session.query(model_cls)

        if query_str:
            sort = False if sort_by else True
            query = search(query_str=query_str, query=query, model=model, sort=sort)

        # Apply model-specific filters directly to the query to avoid intersect ordering issues
        query = apply_model_specific_filters(model_cls, query, current_user, role)

        tag_all_filters = []
        if filter_spec:
            # some functions pass filter_spec as dictionary such as auth/views.py/get_users
            # but most come from API as seraialized JSON
            if isinstance(filter_spec, str):
                filter_spec = json.loads(filter_spec)
            query = apply_filter_specific_joins(model_cls, filter_spec, query)
            # if the filter_spec has the TagAll filter, we need to split the query up
            # and intersect all of the results
            if has_not_case_type(filter_spec):
                new_filter_spec = rebuild_filter_spec_for_not_case_type(filter_spec)
                if new_filter_spec:
                    query = apply_filters(query, new_filter_spec, model_cls)
            if has_tag_all(filter_spec):
                new_filter_spec, tag_all_spec = rebuild_filter_spec_without_tag_all(filter_spec)
                if new_filter_spec:
                    query = apply_filters(query, new_filter_spec, model_cls)
                for tag_filter in tag_all_spec:
                    tag_all_filters.append(apply_filters(query, tag_filter, model_cls))
            else:
                query = apply_filters(query, filter_spec, model_cls)

        # Apply tag_all filters using intersect only when necessary
        for filter in tag_all_filters:
            query = query.intersect(filter)

        if sort_by:
            sort_spec = create_sort_spec(model, sort_by, descending)
            query = apply_sort(query, sort_spec)

    except (FieldNotFound, BadFilterFormat) as e:
        log.error(f"Error building or applying filters: {str(e)}")
        raise e

    if items_per_page == -1:
        items_per_page = None

    # sometimes we get bad input for the search function
    # TODO investigate moving to a different way to parsing queries that won't through errors
    # e.g. websearch_to_tsquery
    # https://www.postgresql.org/docs/current/textsearch-controls.html
    try:
        # Check if this model is likely to have duplicate results from many-to-many joins
        # Models with many secondary relationships (like Tag) can cause count inflation
        models_needing_distinct = ["Tag"]  # Add other models here as needed

        if model in models_needing_distinct and items_per_page is not None:
            # Use custom pagination that handles DISTINCT properly
            from collections import namedtuple

            Pagination = namedtuple(
                "Pagination", ["page_number", "page_size", "num_pages", "total_results"]
            )

            # Get total count using distinct ID to avoid duplicates
            # Remove ORDER BY clause for counting since it's not needed and causes issues with DISTINCT
            count_query = query.with_entities(model_cls.id).distinct().order_by(None)
            total_count = count_query.count()

            # Apply DISTINCT to the main query as well to avoid duplicate results
            # Remove ORDER BY clause since it can conflict with DISTINCT when ordering by joined table columns
            query = query.distinct().order_by(None)

            # Apply pagination to the distinct query
            offset = (page - 1) * items_per_page if page > 1 else 0
            query = query.offset(offset).limit(items_per_page)

            # Calculate number of pages
            num_pages = (
                (total_count + items_per_page - 1) // items_per_page if items_per_page > 0 else 1
            )

            pagination = Pagination(page, items_per_page, num_pages, total_count)
        else:
            # Use standard pagination for other models
            query, pagination = apply_pagination(query, page_number=page, page_size=items_per_page)

    except ProgrammingError as e:
        log.debug(e)
        return {
            "items": [],
            "itemsPerPage": items_per_page,
            "page": page,
            "total": 0,
        }

    return {
        "items": query.all(),
        "itemsPerPage": pagination.page_size,
        "page": pagination.page_number,
        "total": pagination.total_results,
    }


def restricted_incident_filter(query: orm.Query, current_user: DispatchUser, role: UserRoles):
    """Adds additional incident filters to query (usually for permissions)."""
    # Allow unrestricted access for admin roles
    if role in [UserRoles.admin, UserRoles.owner, UserRoles.manager]:
        return query.distinct()

    # For all other roles (including member, none, and any unhandled roles),
    # apply restrictive filtering - default deny approach
    query = (
        query.outerjoin(Participant, Incident.id == Participant.incident_id)
        .outerjoin(IndividualContact, IndividualContact.id == Participant.individual_contact_id)
        .filter(
            or_(
                Incident.visibility == Visibility.open,
                and_(
                    Incident.visibility == Visibility.restricted,
                    IndividualContact.email == current_user.email,
                ),
            )
        )
    )
    return query.distinct()


def restricted_case_filter(query: orm.Query, current_user: DispatchUser, role: UserRoles):
    """Adds additional case filters to query (usually for permissions)."""
    # Allow unrestricted access for admin roles
    if role in [UserRoles.admin, UserRoles.owner, UserRoles.manager]:
        return query.distinct()

    # For all other roles (including member, none, and any unhandled roles),
    # apply restrictive filtering - default deny approach
    query = (
        query.outerjoin(Participant, Case.id == Participant.case_id)
        .outerjoin(IndividualContact, IndividualContact.id == Participant.individual_contact_id)
        .filter(
            or_(
                Case.visibility == Visibility.open,
                and_(
                    Case.visibility == Visibility.restricted,
                    IndividualContact.email == current_user.email,
                ),
            )
        )
    )
    return query.distinct()


def restricted_incident_type_filter(query: orm.Query, current_user: DispatchUser):
    """Adds additional incident type filters to query (usually for permissions)."""
    if current_user:
        query = query.filter(IncidentType.visibility == Visibility.open)
    return query
