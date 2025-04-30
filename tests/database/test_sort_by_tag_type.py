import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from dispatch.database.core import Base
from dispatch.database.service import create_sort_spec, apply_sort, search_filter_sort_paginate
from dispatch.tag.models import Tag
from dispatch.tag_type.models import TagType


class TestSortByTagType:
    def test_sort_by_tag_type_name(self, session):
        """Test that sorting by TagType.name works correctly."""
        # Create tag types
        tag_type1 = TagType(name="A Tag Type", project_id=1)
        tag_type2 = TagType(name="B Tag Type", project_id=1)
        session.add(tag_type1)
        session.add(tag_type2)
        session.commit()

        # Create tags
        tag1 = Tag(name="Tag 1", tag_type=tag_type2, project_id=1)
        tag2 = Tag(name="Tag 2", tag_type=tag_type1, project_id=1)
        session.add(tag1)
        session.add(tag2)
        session.commit()

        # Test sorting by tag_type.name
        result = search_filter_sort_paginate(
            db_session=session,
            model="Tag",
            sort_by=["tag_type.name"],
            descending=[False],
        )

        # Verify that the tags are sorted by tag_type.name
        assert len(result["items"]) == 2
        assert result["items"][0].tag_type.name == "A Tag Type"
        assert result["items"][1].tag_type.name == "B Tag Type"

    def test_sort_by_tag_type_name_with_filter(self, session):
        """Test that sorting by TagType.name works correctly when combined with filtering."""
        # Create tag types with unique names for this test
        tag_type1 = TagType(name="C Tag Type", project_id=1)
        tag_type2 = TagType(name="D Tag Type", project_id=1)
        session.add(tag_type1)
        session.add(tag_type2)
        session.commit()

        # Create tags
        tag1 = Tag(name="Tag 3", tag_type=tag_type2, project_id=1)
        tag2 = Tag(name="Tag 4", tag_type=tag_type1, project_id=1)
        session.add(tag1)
        session.add(tag2)
        session.commit()

        # Test sorting by tag_type.name with a filter
        filter_spec = {
            "and": [
                {"or": [{"field": "name", "op": "==", "value": "Tag 3"}]}
            ]
        }

        result = search_filter_sort_paginate(
            db_session=session,
            model="Tag",
            filter_spec=filter_spec,
            sort_by=["tag_type.name"],
            descending=[False],
        )

        # Verify that the filtered tags are sorted by tag_type.name
        assert len(result["items"]) == 1
        assert result["items"][0].name == "Tag 3"
        assert result["items"][0].tag_type.name == "D Tag Type"
