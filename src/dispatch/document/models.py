from datetime import datetime
from typing import List, Optional

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

# Association tables for many to many relationships
assoc_document_filters = Table(
    "assoc_document_filters",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("document_id", "search_filter_id"),
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


# Pydantic models...
class DocumentBase(ResourceBase, EvergreenBase):
    description: Optional[str] = Field(None, nullable=True)
    name: NameStr
    created_at: Optional[datetime] = Field(None, nullable=True)
    updated_at: Optional[datetime] = Field(None, nullable=True)


class DocumentCreate(DocumentBase):
    filters: Optional[List[SearchFilterRead]] = []
    project: ProjectRead


class DocumentUpdate(DocumentBase):
    filters: Optional[List[SearchFilterRead]]


class DocumentRead(DocumentBase):
    id: PrimaryKey
    filters: Optional[List[SearchFilterRead]] = []
    project: Optional[ProjectRead]

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        if not v:
            return DOCUMENT_DESCRIPTIONS.get(values["resource_type"], "No Description")
        return v


class DocumentPagination(Pagination):
    items: List[DocumentRead] = []
