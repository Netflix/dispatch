from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Optional

from pydantic import validator
from sqlalchemy.sql.sqltypes import Numeric
from dispatch.models import NameStr, PrimaryKey
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType, observes

from dispatch.database.core import Base
from dispatch.enums import Visibility
from dispatch.event.models import EventRead
from dispatch.case_priority.models import (
    CasePriorityBase,
    CasePriorityCreate,
    CasePriorityRead,
)
from dispatch.case_type.models import CaseTypeCreate, CaseTypeRead, CaseTypeBase
from dispatch.models import DispatchBase, ProjectMixin, TimeStampMixin
from dispatch.participant.models import Participant, ParticipantRead, ParticipantUpdate
from dispatch.tag.models import TagRead
from dispatch.ticket.models import TicketRead

from .enums import CaseStatus


assoc_case_tags = Table(
    "assoc_case_tags",
    Base.metadata,
    Column("case_id", Integer, ForeignKey("case.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("case_id", "tag_id"),
)


class Case(Base, TimeStampMixin, ProjectMixin):
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
            "title", "description", "name", weights={"name": "A", "title": "B", "description": "C"}
        )
    )

    # relationships
    assignee_id = Column(Integer, ForeignKey("participant.id"))
    assignee = relationship("Participant", foreign_keys=[assignee_id], post_update=True)

    reporter_id = Column(Integer, ForeignKey("participant.id"))
    reporter = relationship("Participant", foreign_keys=[reporter_id], post_update=True)

    case_priority = relationship("CasePriority", backref="case")
    case_priority_id = Column(Integer, ForeignKey("case_priority.id"))

    case_type = relationship("CaseType", backref="case")
    case_type_id = Column(Integer, ForeignKey("case_type.id"))

    duplicate_id = Column(Integer, ForeignKey("case.id"))
    duplicates = relationship("Case", remote_side=[id], uselist=True)

    tags = relationship(
        "Tag",
        secondary=assoc_case_tags,
        backref="cases",
    )

    tasks = relationship("Task", backref="case", cascade="all, delete-orphan")
    ticket = relationship("Ticket", uselist=False, backref="case", cascade="all, delete-orphan")


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
    assignee: Optional[ParticipantUpdate]
    case_priority: Optional[CasePriorityCreate]
    case_type: Optional[CaseTypeCreate]
    project: ProjectRead
    reporter: Optional[ParticipantUpdate]
    tags: Optional[List[TagRead]] = []


class CaseReadNested(CaseBase):
    id: PrimaryKey
    assignee: Optional[ParticipantRead]
    case_priority: CasePriorityRead
    case_type: CaseTypeRead
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    name: Optional[NameStr]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    reporter: Optional[ParticipantRead]
    stable_at: Optional[datetime] = None


class CaseRead(CaseBase):
    id: PrimaryKey
    assignee: Optional[ParticipantRead]
    case_priority: CasePriorityRead
    case_type: CaseTypeRead
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    duplicates: Optional[List[CaseReadNested]] = []
    events: Optional[List[EventRead]] = []
    name: Optional[NameStr]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    reporter: Optional[ParticipantRead]
    stable_at: Optional[datetime] = None
    tags: Optional[List[TagRead]] = []
    ticket: Optional[TicketRead] = None


class CaseUpdate(CaseBase):
    assignee: Optional[ParticipantUpdate]
    case_priority: CasePriorityBase
    case_type: CaseTypeBase
    duplicates: Optional[List[CaseReadNested]] = []
    reported_at: Optional[datetime] = None
    reporter: Optional[ParticipantUpdate]
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
