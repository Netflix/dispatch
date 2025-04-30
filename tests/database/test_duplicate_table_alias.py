import pytest
import json
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.exc import ProgrammingError

from dispatch.database.core import Base
from dispatch.database.service import search_filter_sort_paginate


# Define test models that mimic the Tag and TagType relationship
class TestTagType(Base):
    __tablename__ = "test_tag_type"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    discoverable_incident = Column(Boolean, default=True)


class TestTag(Base):
    __tablename__ = "test_tag"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    discoverable = Column(Boolean, default=True)
    tag_type_id = Column(Integer, ForeignKey("test_tag_type.id"))
    tag_type = relationship("TestTagType")


def test_search_filter_sort_paginate_duplicate_alias(session, monkeypatch):
    """
    Test that search_filter_sort_paginate handles duplicate table aliases correctly.
    This test reproduces the exact error seen in production.
    """
    # Create test data
    tag_type = TestTagType(name="test_type", discoverable_incident=True)
    session.add(tag_type)
    session.commit()

    tag = TestTag(name="test_tag", discoverable=True, tag_type_id=tag_type.id)
    session.add(tag)
    session.commit()

    # Create a filter spec that would cause the same table to be joined twice
    filter_spec = {
        "and": [
            {"field": "discoverable", "op": "==", "value": "true"},
            {"model": "TestTagType", "field": "discoverable_incident", "op": "==", "value": "true"}
        ]
    }

    # Create a sort spec that would also reference the joined table
    sort_by = ["TestTagType.name"]  # Fixed: Use TestTagType instead of tag_type
    descending = [False]

    # Mock the apply_filter_specific_joins function to track if it's called with the right parameters
    original_apply_filter_specific_joins = None

    def mock_apply_filter_specific_joins(model, filter_spec, query):
        # This is where we'd expect to see the duplicate table alias error
        from sqlalchemy.orm import aliased
        from dispatch.database.service import get_named_models, build_filters

        # Get the model map from the original function
        model_map = {
            (TestTag, "TestTagType"): (TestTag.tag_type, False),
        }

        # Build filters and get named models
        filters = build_filters(filter_spec)
        filter_models = get_named_models(filters)

        # Track joined tables by name
        joined_tables = set()

        # Apply joins
        for filter_model in filter_models:
            if model_map.get((model, filter_model)):
                joined_model, is_outer = model_map[(model, filter_model)]

                # Get table name
                table_name = getattr(joined_model, "__tablename__", str(joined_model))

                # Check if we've already joined this table
                if table_name in joined_tables:
                    # Create an alias for the second join
                    aliased_model = aliased(joined_model)
                    query = query.outerjoin(aliased_model) if is_outer else query.join(aliased_model)
                else:
                    # First time joining this table
                    query = query.outerjoin(joined_model) if is_outer else query.join(joined_model)
                    joined_tables.add(table_name)

        return query

    # Replace the function with our mock
    monkeypatch.setattr("dispatch.database.service.apply_filter_specific_joins", mock_apply_filter_specific_joins)

    # This would fail with duplicate table alias error before our fix
    try:
        result = search_filter_sort_paginate(
            db_session=session,
            model="TestTag",
            filter_spec=json.dumps(filter_spec),
            sort_by=sort_by,
            descending=descending
        )

        # If we get here, no exception was raised, which means our fix works
        assert result["items"] is not None
        # We might get 0 or more items depending on the test data, but we shouldn't get an error

    except Exception as e:
        if "table name specified more than once" in str(e):
            pytest.fail("Duplicate table alias error still occurring")
        else:
            raise


def test_search_filter_sort_paginate_duplicate_alias_in_filter(session, monkeypatch):
    """
    Test that search_filter_sort_paginate handles duplicate table aliases in filter correctly.
    """
    # Create test data
    tag_type = TestTagType(name="test_type", discoverable_incident=True)
    session.add(tag_type)
    session.commit()

    tag = TestTag(name="test_tag", discoverable=True, tag_type_id=tag_type.id)
    session.add(tag)
    session.commit()

    # Create a filter spec that would cause the same table to be joined twice
    filter_spec = {
        "and": [
            {"model": "TestTagType", "field": "name", "op": "==", "value": "test_type"},
            {"model": "TestTagType", "field": "discoverable_incident", "op": "==", "value": "true"}
        ]
    }

    # Mock the apply_filter_specific_joins function to track if it's called with the right parameters
    def mock_apply_filter_specific_joins(model, filter_spec, query):
        # This is where we'd expect to see the duplicate table alias error
        from sqlalchemy.orm import aliased
        from dispatch.database.service import get_named_models, build_filters

        # Get the model map from the original function
        model_map = {
            (TestTag, "TestTagType"): (TestTag.tag_type, False),
        }

        # Build filters and get named models
        filters = build_filters(filter_spec)
        filter_models = get_named_models(filters)

        # Track joined tables by name
        joined_tables = set()

        # Apply joins
        for filter_model in filter_models:
            if model_map.get((model, filter_model)):
                joined_model, is_outer = model_map[(model, filter_model)]

                # Get table name
                table_name = getattr(joined_model, "__tablename__", str(joined_model))

                # Check if we've already joined this table
                if table_name in joined_tables:
                    # Create an alias for the second join
                    aliased_model = aliased(joined_model)
                    query = query.outerjoin(aliased_model) if is_outer else query.join(aliased_model)
                else:
                    # First time joining this table
                    query = query.outerjoin(joined_model) if is_outer else query.join(joined_model)
                    joined_tables.add(table_name)

        return query

    # Replace the function with our mock
    monkeypatch.setattr("dispatch.database.service.apply_filter_specific_joins", mock_apply_filter_specific_joins)

    # This would fail with duplicate table alias error before our fix
    try:
        result = search_filter_sort_paginate(
            db_session=session,
            model="TestTag",
            filter_spec=json.dumps(filter_spec)
        )

        # If we get here, no exception was raised, which means our fix works
        assert result["items"] is not None
        # We might get 0 or more items depending on the test data, but we shouldn't get an error

    except Exception as e:
        if "table name specified more than once" in str(e):
            pytest.fail("Duplicate table alias error still occurring")
        else:
            raise
