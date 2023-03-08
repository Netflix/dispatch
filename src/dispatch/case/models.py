from datetime import datetime
from collections import Counter, defaultdict
from typing import List, Optional, Any, ForwardRef

from pydantic import validator
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
from sqlalchemy_utils import TSVectorType, observes

from dispatch.case.priority.models import (
    CasePriorityRead,
    CasePriorityBase,
)
from dispatch.case.severity.models import CaseSeverityBase, CaseSeverityRead
from dispatch.case.type.models import CaseTypeBase, CaseTypeRead
from dispatch.database.core import Base
from dispatch.document.models import Document, DocumentRead
from dispatch.enums import Visibility
from dispatch.entity.models import EntityRead
from dispatch.event.models import EventRead
from dispatch.group.models import Group, GroupRead
from dispatch.incident.models import IncidentReadMinimal
from dispatch.messaging.strings import CASE_RESOLUTION_DEFAULT
from dispatch.models import DispatchBase, ProjectMixin, TimeStampMixin
from dispatch.models import NameStr, PrimaryKey
from dispatch.participant.models import Participant
from dispatch.participant.models import ParticipantRead, ParticipantReadMinimal, ParticipantUpdate
from dispatch.storage.models import StorageRead
from dispatch.tag.models import TagRead
from dispatch.ticket.models import TicketRead
from dispatch.workflow.models import WorkflowInstanceRead

from .enums import CaseStatus


# Assoc table for case and tags
assoc_case_tags = Table(
    "assoc_case_tags",
    Base.metadata,
    Column("case_id", Integer, ForeignKey("case.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("case_id", "tag_id"),
)

# Assoc table for cases and incidents
assoc_cases_incidents = Table(
    "assoc_case_incidents",
    Base.metadata,
    Column("case_id", Integer, ForeignKey("case.id", ondelete="CASCADE")),
    Column("incident_id", Integer, ForeignKey("incident.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("case_id", "incident_id"),
)


class Case(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    resolution = Column(String, default=CASE_RESOLUTION_DEFAULT, nullable=False)
    status = Column(String, default=CaseStatus.new, nullable=False)
    visibility = Column(String, default=Visibility.open, nullable=False)
    participants_team = Column(String)
    participants_location = Column(String)

    reported_at = Column(DateTime, default=datetime.utcnow)
    triage_at = Column(DateTime)
    escalated_at = Column(DateTime)
    closed_at = Column(DateTime)

    search_vector = Column(
        TSVectorType(
            "name", "title", "description", weights={"name": "A", "title": "B", "description": "C"}
        )
    )

    # relationships
    assignee_id = Column(Integer, ForeignKey("participant.id", ondelete="CASCADE"))
    assignee = relationship(
        Participant, foreign_keys=[assignee_id], lazy="subquery", post_update=True
    )

    case_type = relationship("CaseType", backref="case")
    case_type_id = Column(Integer, ForeignKey("case_type.id"))

    case_severity = relationship("CaseSeverity", backref="case")
    case_severity_id = Column(Integer, ForeignKey("case_severity.id"))

    case_priority = relationship("CasePriority", backref="case")
    case_priority_id = Column(Integer, ForeignKey("case_priority.id"))

    case_document_id = Column(Integer, ForeignKey("document.id"))
    case_document = relationship("Document", foreign_keys=[case_document_id])
    documents = relationship(
        "Document", backref="case", cascade="all, delete-orphan", foreign_keys=[Document.case_id]
    )

    duplicate_id = Column(Integer, ForeignKey("case.id"))
    duplicates = relationship("Case", remote_side=[id], uselist=True, foreign_keys=[duplicate_id])

    events = relationship("Event", backref="case", cascade="all, delete-orphan")

    groups = relationship(
        "Group", backref="case", cascade="all, delete-orphan", foreign_keys=[Group.case_id]
    )

    participants = relationship(
        Participant,
        backref="case",
        cascade="all, delete-orphan",
        foreign_keys=[Participant.case_id],
    )

    incidents = relationship("Incident", secondary=assoc_cases_incidents, backref="cases")

    tactical_group_id = Column(Integer, ForeignKey("group.id"))
    tactical_group = relationship("Group", foreign_keys=[tactical_group_id])

    workflow_instances = relationship(
        "WorkflowInstance", backref="case", cascade="all, delete-orphan"
    )

    conversation = relationship(
        "Conversation", uselist=False, backref="case", cascade="all, delete-orphan"
    )

    related_id = Column(Integer, ForeignKey("case.id"))
    related = relationship("Case", remote_side=[id], uselist=True, foreign_keys=[related_id])

    storage = relationship("Storage", uselist=False, backref="case", cascade="all, delete-orphan")

    tags = relationship(
        "Tag",
        secondary=assoc_case_tags,
        backref="cases",
    )

    ticket = relationship("Ticket", uselist=False, backref="case", cascade="all, delete-orphan")

    @observes("participants")
    def participant_observer(self, participants):
        self.participants_team = Counter(p.team for p in participants).most_common(1)[0][0]
        self.participants_location = Counter(p.location for p in participants).most_common(1)[0][0]


class SignalRead(DispatchBase):
    id: PrimaryKey
    name: str
    owner: str
    description: Optional[str]
    variant: Optional[str]
    external_id: str
    external_url: Optional[str]


class SignalInstanceRead(DispatchBase):
    signal: SignalRead
    entities: Optional[List[EntityRead]] = []
    tags: Optional[List[TagRead]] = []
    raw: Any
    fingerprint: Optional[str]
    created_at: datetime


class ProjectRead(DispatchBase):
    id: Optional[PrimaryKey]
    name: NameStr
    color: Optional[str]


# Pydantic models...
class CaseBase(DispatchBase):
    title: str
    description: Optional[str]
    resolution: Optional[str]
    status: Optional[CaseStatus]
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
    case_priority: Optional[CasePriorityRead]
    case_severity: Optional[CaseSeverityRead]
    case_type: Optional[CaseTypeRead]
    project: Optional[ProjectRead]
    reporter: Optional[ParticipantUpdate]
    tags: Optional[List[TagRead]] = []


CaseReadMinimal = ForwardRef("CaseReadMinimal")


class CaseReadMinimal(CaseBase):
    id: PrimaryKey
    assignee: Optional[ParticipantReadMinimal]
    case_priority: CasePriorityRead
    case_severity: CaseSeverityRead
    case_type: CaseTypeRead
    duplicates: Optional[List[CaseReadMinimal]] = []
    incidents: Optional[List[IncidentReadMinimal]] = []
    related: Optional[List[CaseReadMinimal]] = []
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    name: Optional[NameStr]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    triage_at: Optional[datetime] = None


CaseReadMinimal.update_forward_refs()


class CaseRead(CaseBase):
    id: PrimaryKey
    assignee: Optional[ParticipantRead]
    case_priority: CasePriorityRead
    case_severity: CaseSeverityRead
    case_type: CaseTypeRead
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    documents: Optional[List[DocumentRead]] = []
    duplicates: Optional[List[CaseReadMinimal]] = []
    escalated_at: Optional[datetime] = None
    events: Optional[List[EventRead]] = []
    groups: Optional[List[GroupRead]] = []
    incidents: Optional[List[IncidentReadMinimal]] = []
    name: Optional[NameStr]
    project: ProjectRead
    related: Optional[List[CaseReadMinimal]] = []
    reported_at: Optional[datetime] = None
    participants: Optional[List[ParticipantRead]] = []
    signal_instances: Optional[List[SignalInstanceRead]] = []
    storage: Optional[StorageRead] = None
    tags: Optional[List[TagRead]] = []
    ticket: Optional[TicketRead] = None
    triage_at: Optional[datetime] = None
    workflow_instances: Optional[List[WorkflowInstanceRead]] = []


class CaseUpdate(CaseBase):
    assignee: Optional[ParticipantUpdate]
    case_priority: Optional[CasePriorityBase]
    case_severity: Optional[CaseSeverityBase]
    case_type: Optional[CaseTypeBase]
    duplicates: Optional[List[CaseRead]] = []
    related: Optional[List[CaseRead]] = []
    escalated_at: Optional[datetime] = None
    incidents: Optional[List[IncidentReadMinimal]] = []
    reported_at: Optional[datetime] = None
    tags: Optional[List[TagRead]] = []
    triage_at: Optional[datetime] = None

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
                        "Found multiple exclusive tags. Please ensure that only one tag of a given "
                        f"type is applied. Tags: {','.join([t.name for t in v])}"
                    )
        return v


class CasePagination(DispatchBase):
    items: List[CaseReadMinimal] = []
    itemsPerPage: int
    page: int
    total: int
