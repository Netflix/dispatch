from datetime import datetime
from typing import List, Optional
from collections import defaultdict

from pydantic import validator, Field
from dispatch.models import EvergreenBase, NameStr, PrimaryKey
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.messaging.strings import DOCUMENT_DESCRIPTIONS
from dispatch.models import ResourceBase, ProjectMixin, ResourceMixin, EvergreenMixin, Pagination
from dispatch.project.models import ProjectRead
from dispatch.search_filter.models import SearchFilterRead
from dispatch.tag.models import TagRead


# Association tables for many to many relationships
assoc_document_filters = Table(
    "assoc_document_filters",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("document_id", "search_filter_id"),
)

assoc_document_tags = Table(
    "assoc_document_tags",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("document_id", "tag_id"),
)


class Document(ProjectMixin, ResourceMixin, EvergreenMixin, Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    report_id = Column(Integer, ForeignKey("report.id", ondelete="CASCADE"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE", use_alter=True))
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE", use_alter=True))

    filters = relationship("SearchFilter", secondary=assoc_document_filters, backref="documents")

    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))
    tags = relationship(
        "Tag",
        secondary=assoc_document_tags,
        lazy="subquery",
        backref="documents",
    )


# Pydantic models...
class DocumentBase(ResourceBase, EvergreenBase):
    description: Optional[str] = Field(None, nullable=True)
    name: NameStr
    created_at: Optional[datetime] = Field(None, nullable=True)
    updated_at: Optional[datetime] = Field(None, nullable=True)


class DocumentCreate(DocumentBase):
    filters: Optional[List[SearchFilterRead]] = []
    project: ProjectRead
    tags: Optional[List[TagRead]] = []


class DocumentUpdate(DocumentBase):
    filters: Optional[List[SearchFilterRead]]
    tags: Optional[List[TagRead]] = []

    @validator("tags")
    def find_exclusive(cls, v):
        if v:
            exclusive_tags = defaultdict(list)
            for tag in v:
                if tag.tag_type.exclusive:
                    exclusive_tags[tag.tag_type.id].append(tag)

            for tag_types in exclusive_tags.values():
                if len(tag_types) > 1:
                    raise ValueError(
                        f"Found multiple exclusive tags. Please ensure that only one tag of a given type is applied. Tags: {','.join([t.name for t in v])}"  # noqa: E501
                    )
        return v


class DocumentRead(DocumentBase):
    id: PrimaryKey
    filters: Optional[List[SearchFilterRead]] = []
    project: Optional[ProjectRead]
    tags: Optional[List[TagRead]] = []

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        if not v:
            return DOCUMENT_DESCRIPTIONS.get(values["resource_type"], "No Description")
        return v


class DocumentPagination(Pagination):
    items: List[DocumentRead] = []
