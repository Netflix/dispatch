from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin, PrimaryKey, Pagination
from dispatch.project.models import ProjectRead
from dispatch.tag_type.models import TagTypeRead, TagTypeCreate, TagTypeUpdate


class Tag(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    uri = Column(String)
    source = Column(String)
    external_id = Column(String)
    discoverable = Column(Boolean, default=True)

    # Relationships
    tag_type_id = Column(Integer, ForeignKey("tag_type.id"), nullable=False)
    tag_type = relationship("TagType", backref="tag")

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(
        TSVectorType("name", "description", "external_id", regconfig="pg_catalog.simple")
    )


# Pydantic models
class TagBase(DispatchBase):
    name: str | None = None
    source: str | None = None
    uri: str | None = None
    discoverable: bool | None = True
    external_id: str | None = None
    description: str | None = None


class TagCreate(TagBase):
    id: PrimaryKey | None = None
    tag_type: TagTypeCreate
    project: ProjectRead


class TagUpdate(TagBase):
    id: PrimaryKey | None = None
    tag_type: TagTypeUpdate | None = None


class TagRead(TagBase):
    id: PrimaryKey
    tag_type: TagTypeRead | None = None
    project: ProjectRead


class TagPagination(Pagination):
    items: list[TagRead]


# Tag recommendation models
class TagRecommendation(DispatchBase):
    """Model for a single tag recommendation."""

    id: PrimaryKey
    name: str
    reason: str


class TagTypeRecommendation(DispatchBase):
    """Model for tag recommendations grouped by tag type."""

    tag_type_id: PrimaryKey
    tags: list[TagRecommendation]


class TagRecommendationResponse(DispatchBase):
    """Response model for tag recommendations."""

    recommendations: list[TagTypeRecommendation]
