from datetime import datetime

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
    description: str | None = Field(None, nullable=True)
    name: NameStr
    created_at: datetime | None = Field(None, nullable=True)
    updated_at: datetime | None = Field(None, nullable=True)


class DocumentCreate(DocumentBase):
    filters: list[SearchFilterRead] = []
    project: ProjectRead


class DocumentUpdate(DocumentBase):
    filters: list[SearchFilterRead] = []


class DocumentRead(DocumentBase):
    id: PrimaryKey
    filters: list[SearchFilterRead] = []
    project: ProjectRead | None

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        if not v:
            return DOCUMENT_DESCRIPTIONS.get(values["resource_type"], "No Description")
        return v


class DocumentPagination(Pagination):
    items: list[DocumentRead] = []
