from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, ForwardRef, List, Optional

from pydantic import Field, validator
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType, observes

from dispatch.case_cost.models import (
    CaseCostRead,
    CaseCostUpdate,
)
from dispatch.case.priority.models import CasePriorityBase, CasePriorityCreate, CasePriorityRead
from dispatch.case.severity.models import CaseSeverityBase, CaseSeverityCreate, CaseSeverityRead
from dispatch.case.type.models import CaseTypeBase, CaseTypeCreate, CaseTypeRead
from dispatch.conversation.models import ConversationRead
from dispatch.database.core import Base
from dispatch.document.models import Document, DocumentRead
from dispatch.entity.models import EntityRead
from dispatch.enums import Visibility
from dispatch.event.models import EventRead
from dispatch.group.models import Group, GroupRead
from dispatch.incident.models import IncidentReadMinimal
from dispatch.messaging.strings import CASE_RESOLUTION_DEFAULT
from dispatch.models import (
    DispatchBase,
    NameStr,
    PrimaryKey,
    ProjectMixin,
    TimeStampMixin,
    Pagination,
)
from dispatch.participant.models import (
    Participant,
    ParticipantRead,
    ParticipantReadMinimal,
    ParticipantUpdate,
)

from dispatch.storage.models import StorageRead
from dispatch.tag.models import TagRead
from dispatch.ticket.models import TicketRead
from dispatch.workflow.models import WorkflowInstanceRead

from .enums import CaseResolutionReason, CaseStatus

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
    resolution_reason = Column(String)
    status = Column(String, default=CaseStatus.new, nullable=False)
    visibility = Column(String, default=Visibility.open, nullable=False)
    participants_team = Column(String)
    participants_location = Column(String)

    reported_at = Column(DateTime, default=datetime.utcnow)
    triage_at = Column(DateTime)
    escalated_at = Column(DateTime)
    closed_at = Column(DateTime)

    dedicated_channel = Column(Boolean, default=False)

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

    reporter_id = Column(Integer, ForeignKey("participant.id", ondelete="CASCADE"))
    reporter = relationship(
        Participant, foreign_keys=[reporter_id], lazy="subquery", post_update=True
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

    signal_thread_ts = Column(String, nullable=True)

    storage = relationship("Storage", uselist=False, backref="case", cascade="all, delete-orphan")

    tags = relationship(
        "Tag",
        secondary=assoc_case_tags,
        backref="cases",
    )

    ticket = relationship("Ticket", uselist=False, backref="case", cascade="all, delete-orphan")

    # resources
    case_costs = relationship(
        "CaseCost",
        backref="case",
        cascade="all, delete-orphan",
        lazy="subquery",
        order_by="CaseCost.created_at",
    )

    @observes("participants")
    def participant_observer(self, participants):
        self.participants_team = Counter(p.team for p in participants).most_common(1)[0][0]
        self.participants_location = Counter(p.location for p in participants).most_common(1)[0][0]

    @property
    def has_channel(self) -> bool:
        if not self.conversation:
            return False
        return True if not self.conversation.thread_id else False

    @property
    def has_thread(self) -> bool:
        if not self.conversation:
            return False
        return True if self.conversation.thread_id else False

    @hybrid_property
    def total_cost(self):
        total_cost = 0
        if self.case_costs:
            for cost in self.case_costs:
                total_cost += cost.amount
        return total_cost


class SignalRead(DispatchBase):
    id: PrimaryKey
    name: str
    owner: str
    description: Optional[str]
    variant: Optional[str]
    external_id: str
    external_url: Optional[str]
    workflow_instances: Optional[List[WorkflowInstanceRead]] = []


class SignalInstanceRead(DispatchBase):
    created_at: datetime
    entities: Optional[List[EntityRead]] = []
    raw: Any
    signal: SignalRead
    tags: Optional[List[TagRead]] = []


class ProjectRead(DispatchBase):
    id: Optional[PrimaryKey]
    name: NameStr
    color: Optional[str]
    allow_self_join: Optional[bool] = Field(True, nullable=True)


# Pydantic models...
class CaseBase(DispatchBase):
    title: str
    description: Optional[str]
    resolution: Optional[str]
    resolution_reason: Optional[CaseResolutionReason]
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
    case_priority: Optional[CasePriorityCreate]
    case_severity: Optional[CaseSeverityCreate]
    case_type: Optional[CaseTypeCreate]
    dedicated_channel: Optional[bool]
    project: Optional[ProjectRead]
    reporter: Optional[ParticipantUpdate]
    tags: Optional[List[TagRead]] = []


CaseReadMinimal = ForwardRef("CaseReadMinimal")


class CaseReadMinimal(CaseBase):
    id: PrimaryKey
    assignee: Optional[ParticipantReadMinimal]
    case_costs: Optional[List[CaseCostRead]] = []
    case_priority: CasePriorityRead
    case_severity: CaseSeverityRead
    case_type: CaseTypeRead
    duplicates: Optional[List[CaseReadMinimal]] = []
    incidents: Optional[List[IncidentReadMinimal]] = []
    related: Optional[List[CaseReadMinimal]] = []
    closed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    dedicated_channel: Optional[bool]
    name: Optional[NameStr]
    project: ProjectRead
    reporter: Optional[ParticipantReadMinimal]
    reported_at: Optional[datetime] = None
    triage_at: Optional[datetime] = None


CaseReadMinimal.update_forward_refs()


class CaseRead(CaseBase):
    id: PrimaryKey
    assignee: Optional[ParticipantRead]
    case_costs: Optional[List[CaseCostRead]] = []
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
    conversation: Optional[ConversationRead] = None
    name: Optional[NameStr]
    project: ProjectRead
    related: Optional[List[CaseReadMinimal]] = []
    reporter: Optional[ParticipantRead]
    reported_at: Optional[datetime] = None
    participants: Optional[List[ParticipantRead]] = []
    signal_instances: Optional[List[SignalInstanceRead]] = []
    storage: Optional[StorageRead] = None
    tags: Optional[List[TagRead]] = []
    ticket: Optional[TicketRead] = None
    triage_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    workflow_instances: Optional[List[WorkflowInstanceRead]] = []


class CaseUpdate(CaseBase):
    assignee: Optional[ParticipantUpdate]
    case_costs: Optional[List[CaseCostUpdate]] = []
    case_priority: Optional[CasePriorityBase]
    case_severity: Optional[CaseSeverityBase]
    case_type: Optional[CaseTypeBase]
    closed_at: Optional[datetime] = None
    duplicates: Optional[List[CaseRead]] = []
    related: Optional[List[CaseRead]] = []
    reporter: Optional[ParticipantUpdate]
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


class CasePagination(Pagination):
    items: List[CaseReadMinimal] = []


class CaseExpandedPagination(Pagination):
    items: List[CaseRead] = []
