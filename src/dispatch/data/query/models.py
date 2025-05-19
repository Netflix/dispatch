from pydantic import Field

from sqlalchemy import Column, Integer, String, Table, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import (
    DispatchBase,
    ProjectMixin,
    Pagination,
    TimeStampMixin,
    PrimaryKey,
)
from dispatch.project.models import ProjectRead
from dispatch.data.source.models import SourceRead

from dispatch.tag.models import TagRead


assoc_query_tags = Table(
    "assoc_query_tags",
    Base.metadata,
    Column("query_id", Integer, ForeignKey("query.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("query_id", "tag_id"),
)

assoc_query_incidents = Table(
    "assoc_query_incidents",
    Base.metadata,
    Column("query_id", Integer, ForeignKey("query.id", ondelete="CASCADE")),
    Column("incident_id", Integer, ForeignKey("incident.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("query_id", "incident_id"),
)


class Query(Base, TimeStampMixin, ProjectMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    text = Column(String)
    language = Column(String)
    source_id = Column(Integer, ForeignKey("source.id"))
    source = relationship("Source", backref="queries")
    tags = relationship("Tag", secondary=assoc_query_tags, backref="queries")
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


# Pydantic models
class QueryBase(DispatchBase):
    name: str | None = Field(None, nullable=False)
    description: str | None = None
    language: str | None = None
    text: str | None = None
    tags: list[TagRead | None] = []
    source: SourceRead
    project: ProjectRead


class QueryCreate(QueryBase):
    pass


class QueryUpdate(QueryBase):
    id: PrimaryKey | None = None


class QueryRead(QueryBase):
    id: PrimaryKey


class QueryPagination(Pagination):
    items: list[QueryRead]
