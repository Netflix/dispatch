import pytest
import json
from json.decoder import JSONDecodeError
from sqlalchemy_filters.exceptions import BadFilterFormat

from dispatch.database.service import (
    Operator,
    Filter,
    search_filter_sort_paginate,
    restricted_incident_filter,
    apply_filters,
)
from dispatch.incident.models import Incident
from dispatch.enums import UserRoles, Visibility


# Test the Filter class and related functions
def test_operator_invalid():
    """Tests that invalid operators raise BadFilterFormat."""
    with pytest.raises(BadFilterFormat):
        Operator("invalid_operator")


def test_filter_missing_field():
    """Tests that missing field raises BadFilterFormat."""
    with pytest.raises(BadFilterFormat):
        Filter({})


def test_filter_invalid_spec():
    """Tests that invalid filter spec raises BadFilterFormat."""
    with pytest.raises(BadFilterFormat):
        Filter(None)


# Test search_filter_sort_paginate
def test_search_filter_sort_paginate_basic(session, user):
    """Tests basic functionality of search_filter_sort_paginate."""
    result = search_filter_sort_paginate(
        db_session=session, model="Incident", current_user=user, role=UserRoles.member
    )

    assert isinstance(result, dict)
    assert "items" in result
    assert "itemsPerPage" in result
    assert "page" in result
    assert "total" in result


def test_basic_pagination(session, incidents, admin_user):
    """Test basic pagination functionality."""
    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        page=1,
        items_per_page=2,
        current_user=admin_user,
        role=UserRoles.admin,
    )

    assert result["page"] == 1
    assert result["itemsPerPage"] == 2
    assert len(result["items"]) == 2


def test_simple_filter_specification(session, incidents, admin_user):
    """Test filtering with simple filter specification."""
    filter_spec = {"field": "visibility", "op": "==", "value": "open"}

    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        filter_spec=json.dumps(filter_spec),
        current_user=admin_user,
        role=UserRoles.admin,
    )

    assert all(incident.visibility == Visibility.open for incident in result["items"])


def test_sorting_functionality(session, incidents, user):
    """Test sorting functionality."""
    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        sort_by=["title"],
        descending=[True],
        current_user=user,
    )

    titles = [incident.title for incident in result["items"]]
    assert titles == sorted(titles, reverse=True)


def test_unlimited_pagination(session, incidents, admin_user):
    """Test pagination with unlimited items per page."""
    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        items_per_page=-1,
        current_user=admin_user,
        role=UserRoles.admin,
    )

    assert len(result["items"]) == result["total"]  # All items


def test_empty_query_string(session, incidents, admin_user):
    """Test behavior with empty query string."""
    result = search_filter_sort_paginate(
        db_session=session,
        model="Incident",
        query_str="",
        current_user=admin_user,
        role=UserRoles.admin,
    )

    assert len(result["items"]) > 0  # Should return all items


def test_invalid_filter_spec(session, incidents, user):
    """Test behavior with invalid filter specification."""
    with pytest.raises(JSONDecodeError):  # Adjust exception type as needed
        search_filter_sort_paginate(
            db_session=session,
            model="Incident",
            filter_spec="invalid_json",
            current_user=user,
        )


def test_pagination_out_of_bounds(session, incidents, user):
    """Test pagination when page number is out of bounds."""
    result = search_filter_sort_paginate(
        db_session=session, model="Incident", page=999, items_per_page=5, current_user=user
    )

    assert len(result["items"]) == 0
    assert result["page"] == 999


def test_role_based_filtering(session, incidents, user, admin_user):
    """Test filtering based on user role."""
    # Test admin access
    admin_result = search_filter_sort_paginate(
        db_session=session, model="Incident", current_user=admin_user, role=UserRoles.admin
    )

    # Test member access
    member_result = search_filter_sort_paginate(
        db_session=session, model="Incident", current_user=user, role=UserRoles.member
    )

    assert len(admin_result["items"]) >= len(member_result["items"])


def test_include_keys_functionality(session, case, admin_user):
    """Test functionality of include_keys parameter."""
    from dispatch.common.utils.views import create_pydantic_include
    from dispatch.case.models import CasePagination

    result = search_filter_sort_paginate(
        db_session=session,
        model="Case",
        include_keys=["tags"],
        current_user=admin_user,
        role=UserRoles.admin,
    )

    # make sure they are renderable
    include_sets = create_pydantic_include(["tags", "title"])

    include_fields = {
        "items": {"__all__": include_sets},
        "itemsPerPage": ...,
        "page": ...,
        "total": ...,
    }
    marshalled = json.loads(CasePagination(**result).json(include=include_fields))
    assert "tags" in marshalled["items"][0].keys()


# Test restricted filters
def test_restricted_incident_filter_member(session, user):
    """Tests incident filtering for member role."""
    query = session.query(Incident)
    filtered_query = restricted_incident_filter(
        query=query, current_user=user, role=UserRoles.member
    )

    assert filtered_query is not None


def test_restricted_incident_filter_admin(session, user):
    """Tests incident filtering for admin role."""
    query = session.query(Incident)
    filtered_query = restricted_incident_filter(
        query=query, current_user=user, role=UserRoles.admin
    )

    assert filtered_query is not None


# Test apply_filters
def test_apply_filters_basic(session):
    """Tests basic filter application."""
    query = session.query(Incident)
    filter_spec = {"field": "title", "op": "==", "value": "Test"}

    filtered_query = apply_filters(query, filter_spec)
    assert filtered_query is not None


def test_apply_filters_complex(session):
    """Tests complex filter application with boolean operations."""
    query = session.query(Incident)
    filter_spec = {
        "and": [
            {"field": "title", "op": "==", "value": "Test"},
            {"field": "visibility", "op": "==", "value": "open"},
        ]
    }

    filtered_query = apply_filters(query, filter_spec)
    assert filtered_query is not None
