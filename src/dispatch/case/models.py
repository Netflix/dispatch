from datetime import datetime
from collections import defaultdict
from typing import List, Optional

from pydantic import validator
from dispatch.models import NameStr, PrimaryKey
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.auth.models import UserRead
from dispatch.case.priority.models import CasePriorityRead
from dispatch.case.severity.models import CaseSeverityRead
from dispatch.case.type.models import CaseTypeRead
from dispatch.data.source.models import SourceRead
from dispatch.database.core import Base
from dispatch.enums import Visibility
from dispatch.event.models import EventRead
from dispatch.incident.models import IncidentRead
from dispatch.models import DispatchBase, ProjectMixin, TimeStampMixin
from dispatch.tag.models import TagRead
from dispatch.ticket.models import TicketRead

from .enums import CaseStatus


# Assoc object for case and case types
class AssocCaseCaseType(Base):
    __tablename__ = "assoc_case_case_type"
    case_id = Column(Integer, ForeignKey("case.id"), primary_key=True)
    case_type_id = Column(Integer, ForeignKey("case_type.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    case_type = relationship("CaseType")


# Assoc object for case and case priorities
class AssocCaseCasePriority(Base):
    __tablename__ = "assoc_case_case_priority"
    case_id = Column(Integer, ForeignKey("case.id"), primary_key=True)
    case_priority_id = Column(Integer, ForeignKey("case_priority.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    case_priority = relationship("CasePriority")


# Assoc object for case and case severities
class AssocCaseCaseSeverity(Base):
    __tablename__ = "assoc_case_case_severity"
    case_id = Column(Integer, ForeignKey("case.id"), primary_key=True)
    case_severity_id = Column(Integer, ForeignKey("case_severity.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    case_severity = relationship("CaseSeverity")


# Assoc table for case and tags
assoc_case_tags = Table(
    "assoc_case_tags",
    Base.metadata,
    Column("case_id", Integer, ForeignKey("case.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("case_id", "tag_id"),
)


class Case(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    resolution = Column(String)
    status = Column(String, default=CaseStatus.active)
    visibility = Column(String, default=Visibility.open, nullable=False)

    # auto generated
    reported_at = Column(DateTime, default=datetime.utcnow)
    stable_at = Column(DateTime)
    closed_at = Column(DateTime)

    search_vector = Column(
        TSVectorType(
            "name", "title", "description", weights={"name": "A", "title": "B", "description": "C"}
        )
    )

    # relationships
    assignee_id = Column(Integer, ForeignKey("dispatch_core.dispatch_user.id"))
    assignee = relationship("DispatchUser", foreign_keys=[assignee_id], post_update=True)

    case_types = relationship("AssocCaseCaseType", backref="cases")
    case_priorities = relationship("AssocCaseCasePriority", backref="cases")
    case_severities = relationship("AssocCaseCaseSeverity", backref="cases")

    duplicate_id = Column(Integer, ForeignKey("case.id"))
    duplicates = relationship("Case", remote_side=[id], uselist=True)
    # events = relationship("Event", backref="case", cascade="all, delete-orphan")
    incident = relationship("Incident", uselist=False, backref="case", cascade="all, delete-orphan")
    source = relationship("Source", uselist=False, backref="case")
    source_id = Column(Integer, ForeignKey("source.id"))
    tags = relationship(
        "Tag",
        secondary=assoc_case_tags,
        backref="cases",
    )
    # tasks = relationship("Task", backref="case", cascade="all, delete-orphan")
    ticket = relationship("Ticket", uselist=False, backref="case", cascade="all, delete-orphan")
    # workflow_instances = relationship(
    #     "WorkflowInstance", backref="case", cascade="all, delete-orphan"
    # )


class ProjectRead(DispatchBase):
    id: Optional[PrimaryKey]
    name: NameStr
    color: Optional[str]


# Pydantic models...
class CaseBase(DispatchBase):
    title: str
    description: str
    resolution: Optional[str]
    status: Optional[CaseStatus] = CaseStatus.active
    visibility: Optional[Visibility]

    @validator("title")
    def title_required(cls, v):
        if not v:
            raise ValueError("must not be empty string")
        return v

    @validator("description")
    def description_required(cls, v):
        if not v:
            raise ValueError("must not be empty string")
        return v


class CaseCreate(CaseBase):
    assignee: Optional[UserRead]
    # case_priority: Optional[CasePriorityCreate]
    # case_type: Optional[CaseTypeCreate]
    project: ProjectRead
    source: SourceRead
    tags: Optional[List[TagRead]] = []


class CaseReadNested(CaseBase):
    id: PrimaryKey
    assignee: Optional[UserRead]
    case_priorities: CasePriorityRead
    case_severities: CaseSeverityRead
    case_types: CaseTypeRead
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    name: Optional[NameStr]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    source: SourceRead
    stable_at: Optional[datetime] = None


class CaseRead(CaseBase):
    id: PrimaryKey
    assignee: UserRead
    # case_priority: CasePriorityRead
    # case_type: CaseTypeRead
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    duplicates: Optional[List[CaseReadNested]] = []
    events: Optional[List[EventRead]] = []
    incident: Optional[IncidentRead]
    name: Optional[NameStr]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    source: SourceRead
    stable_at: Optional[datetime] = None
    tags: Optional[List[TagRead]] = []
    ticket: Optional[TicketRead] = None


class CaseUpdate(CaseBase):
    assignee: Optional[UserRead]
    # case_priority: CasePriorityBase
    # case_type: CaseTypeBase
    duplicates: Optional[List[CaseReadNested]] = []
    incident: Optional[IncidentRead]
    reported_at: Optional[datetime] = None
    source: Optional[SourceRead]
    stable_at: Optional[datetime] = None
    tags: Optional[List[TagRead]] = []

    @validator("tags")
    def find_exclusive(cls, v):
        if v:
            exclusive_tags = defaultdict(list)
            for t in v:
                if t.tag_type.exclusive:
                    exclusive_tags[t.tag_type.id].append(t)

            for v in exclusive_tags.values():
                if len(v) > 1:
                    raise ValueError(
                        f"Found multiple exclusive tags. Please ensure that only one tag of a given type is applied. Tags: {','.join([t.name for t in v])}"
                    )
        return v


class CasePagination(DispatchBase):
    items: List[CaseRead] = []
    itemsPerPage: int
    page: int
    total: int
