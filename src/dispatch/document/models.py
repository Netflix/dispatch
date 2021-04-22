from datetime import datetime
from typing import List, Optional

from pydantic import validator
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base

from dispatch.messaging.strings import INCIDENT_DOCUMENT_DESCRIPTIONS
from dispatch.models import (
    DispatchBase,
    ProjectMixin,
    ResourceMixin,
)

from dispatch.search_filter.models import SearchFilterRead
from dispatch.project.models import ProjectRead

# Association tables for many to many relationships
assoc_document_filters = Table(
    "assoc_document_filters",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("document_id", "search_filter_id"),
)


class Document(ProjectMixin, ResourceMixin, Base):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    report_id = Column(Integer, ForeignKey("report.id"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))

    filters = relationship("SearchFilter", secondary=assoc_document_filters, backref="documents")

    evergreen = Column(Boolean)
    evergreen_owner = Column(String)
    evergreen_reminder_interval = Column(Integer, default=90)  # number of days
    evergreen_last_reminder_at = Column(DateTime)

    search_vector = Column(TSVectorType("name"))


# Pydantic models...
class DocumentBase(DispatchBase):
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    weblink: str
    name: str
    evergreen: Optional[bool] = False
    evergreen_reminder_interval: Optional[int] = 90
    evergreen_last_reminder_at: Optional[datetime] = None
    evergreen_owner: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DocumentCreate(DocumentBase):
    filters: Optional[List[SearchFilterRead]]
    project: Optional[ProjectRead]


class DocumentUpdate(DocumentBase):
    filters: Optional[List[SearchFilterRead]]


class DocumentRead(DocumentBase):
    id: int
    filters: Optional[List[SearchFilterRead]]
    project: Optional[ProjectRead]

    @validator("description", pre=True, always=True)
    def set_description(cls, v, values):
        """Sets the description"""
        if not v:
            return INCIDENT_DOCUMENT_DESCRIPTIONS.get(values["resource_type"], "No Description")
        return v


class DocumentNested(DocumentRead):
    pass


class DocumentPagination(DispatchBase):
    total: int
    items: List[DocumentRead] = []
