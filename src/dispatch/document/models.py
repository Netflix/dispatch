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
    event,
    func,
    extract,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref, relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.incident_priority.models import IncidentPriorityCreate, IncidentPriorityRead
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead
from dispatch.messaging import INCIDENT_DOCUMENT_DESCRIPTIONS
from dispatch.models import DispatchBase, ResourceMixin, TermNested, TermReadNested, TimeStampMixin

# Association tables for many to many relationships
assoc_document_incident_priorities = Table(
    "document_incident_priority",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
    PrimaryKeyConstraint("incident_priority_id", "document_id"),
)

assoc_document_incident_types = Table(
    "document_incident_type",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
    PrimaryKeyConstraint("incident_type_id", "document_id"),
)

assoc_document_incidents = Table(
    "document_incident",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
    PrimaryKeyConstraint("incident_id", "document_id"),
)

assoc_document_terms = Table(
    "document_terms",
    Base.metadata,
    Column("term_id", Integer, ForeignKey("term.id")),
    Column("document_id", Integer, ForeignKey("document.id")),
    PrimaryKeyConstraint("term_id", "document_id"),
)


class Document(Base, ResourceMixin, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    report_id = Column(Integer, ForeignKey("report.id"))
    incident_priorities = relationship(
        "IncidentPriority", secondary=assoc_document_incident_priorities, backref="documents"
    )
    incident_types = relationship(
        "IncidentType", secondary=assoc_document_incident_types, backref="documents"
    )
    terms = relationship(
        "Term", secondary=assoc_document_terms, backref=backref("documents", cascade="all")
    )

    evergreen = Column(Boolean)
    evergreen_owner = Column(String)
    evergreen_reminder_interval = Column(Integer, default=90)  # number of days
    evergreen_last_reminder_at = Column(DateTime)

    @hybrid_property
    def evergreen_is_overdue(self):
        """Determines if we are eligible for a evergreen notification."""
        seconds_since_notified = func.trunc(
            (
                extract("epoch", datetime.utcnow()),
                extract("epoch", self.evergreen_last_reminder_at),
            )
        )
        days_since_notified = seconds_since_notified / 3600 / 24
        return days_since_notified >= self.evergreen_reminder_interval

    search_vector = Column(TSVectorType("name"))


@event.listens_for(Document.evergreen, "set")
def _reset_last_notified(target, value, oldvalue, initiator):
    """Ensures that the last notified is reset if we "enable" the reminder from a disabled state"""
    if value:
        target.evergreen_last_reminder_at = datetime.utcnow()


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
    terms: Optional[List[TermNested]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []


class DocumentUpdate(DocumentBase):
    terms: Optional[List[TermNested]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []


class DocumentRead(DocumentBase):
    id: int
    incident_priorities: Optional[List[IncidentPriorityRead]] = []
    incident_types: Optional[List[IncidentTypeRead]] = []
    terms: Optional[List[TermReadNested]] = []

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
