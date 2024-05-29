from collections import Counter, defaultdict
from datetime import datetime
from typing import ForwardRef, List, Optional

from pydantic import validator, Field, AnyHttpUrl

from sqlalchemy import Column, DateTime, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType, observes

from dispatch.conference.models import ConferenceRead
from dispatch.conversation.models import ConversationRead
from dispatch.database.core import Base
from dispatch.document.models import Document, DocumentRead
from dispatch.enums import Visibility
from dispatch.event.models import EventRead
from dispatch.group.models import Group
from dispatch.incident.priority.models import (
    IncidentPriorityBase,
    IncidentPriorityCreate,
    IncidentPriorityRead,
    IncidentPriorityReadMinimal,
)
from dispatch.incident.severity.models import (
    IncidentSeverityBase,
    IncidentSeverityCreate,
    IncidentSeverityRead,
    IncidentSeverityReadMinimal,
)
from dispatch.incident.type.models import (
    IncidentTypeBase,
    IncidentTypeCreate,
    IncidentTypeRead,
    IncidentTypeReadMinimal,
)
from dispatch.incident_cost.models import (
    IncidentCostRead,
    IncidentCostUpdate,
)
from dispatch.messaging.strings import INCIDENT_RESOLUTION_DEFAULT
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
from dispatch.report.enums import ReportTypes
from dispatch.report.models import ReportRead
from dispatch.storage.models import StorageRead
from dispatch.tag.models import TagRead
from dispatch.task.enums import TaskStatus
from dispatch.term.models import TermRead
from dispatch.ticket.models import TicketRead
from dispatch.workflow.models import WorkflowInstanceRead

from .enums import IncidentStatus

assoc_incident_terms = Table(
    "assoc_incident_terms",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id", ondelete="CASCADE")),
    Column("term_id", Integer, ForeignKey("term.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("incident_id", "term_id"),
)

assoc_incident_tags = Table(
    "assoc_incident_tags",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("incident_id", "tag_id"),
)


class Incident(Base, TimeStampMixin, ProjectMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    resolution = Column(String, default=INCIDENT_RESOLUTION_DEFAULT, nullable=False)
    status = Column(String, default=IncidentStatus.active, nullable=False)
    visibility = Column(String, default=Visibility.open, nullable=False)
    participants_team = Column(String)
    participants_location = Column(String)
    commanders_location = Column(String)
    reporters_location = Column(String)
    delay_executive_report_reminder = Column(DateTime, nullable=True)
    delay_tactical_report_reminder = Column(DateTime, nullable=True)

    # auto generated
    reported_at = Column(DateTime, default=datetime.utcnow)
    stable_at = Column(DateTime)
    closed_at = Column(DateTime)

    search_vector = Column(
        TSVectorType(
            "title", "description", "name", weights={"name": "A", "title": "B", "description": "C"}
        )
    )

    @hybrid_property
    def tactical_reports(self):
        if self.reports:
            tactical_reports = [
                report for report in self.reports if report.type == ReportTypes.tactical_report
            ]
            return tactical_reports

    @hybrid_property
    def last_tactical_report(self):
        if self.tactical_reports:
            return sorted(self.tactical_reports, key=lambda r: r.created_at)[-1]

    @hybrid_property
    def executive_reports(self):
        if self.reports:
            executive_reports = [
                report for report in self.reports if report.type == ReportTypes.executive_report
            ]
            return executive_reports

    @hybrid_property
    def last_executive_report(self):
        if self.executive_reports:
            return sorted(self.executive_reports, key=lambda r: r.created_at)[-1]

    # resources
    incident_costs = relationship(
        "IncidentCost",
        backref="incident",
        cascade="all, delete-orphan",
        lazy="subquery",
        order_by="IncidentCost.created_at",
    )

    incident_priority = relationship("IncidentPriority", backref="incident")
    incident_priority_id = Column(Integer, ForeignKey("incident_priority.id"))

    incident_severity = relationship("IncidentSeverity", backref="incident")
    incident_severity_id = Column(Integer, ForeignKey("incident_severity.id"))

    incident_type = relationship("IncidentType", backref="incident")
    incident_type_id = Column(Integer, ForeignKey("incident_type.id"))

    conference = relationship(
        "Conference", uselist=False, backref="incident", cascade="all, delete-orphan"
    )
    conversation = relationship(
        "Conversation", uselist=False, backref="incident", cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document",
        backref="incident",
        cascade="all, delete-orphan",
        foreign_keys=[Document.incident_id],
    )
    events = relationship("Event", backref="incident", cascade="all, delete-orphan")
    feedback = relationship("Feedback", backref="incident", cascade="all, delete-orphan")
    groups = relationship(
        "Group", backref="incident", cascade="all, delete-orphan", foreign_keys=[Group.incident_id]
    )
    participants = relationship(
        "Participant",
        backref="incident",
        cascade="all, delete-orphan",
        foreign_keys=[Participant.incident_id],
    )
    reports = relationship("Report", backref="incident", cascade="all, delete-orphan")
    storage = relationship(
        "Storage", uselist=False, backref="incident", cascade="all, delete-orphan"
    )
    tags = relationship(
        "Tag",
        secondary=assoc_incident_tags,
        lazy="subquery",
        backref="incidents",
    )
    tasks = relationship("Task", backref="incident", cascade="all, delete-orphan")
    terms = relationship("Term", secondary=assoc_incident_terms, backref="incidents")
    ticket = relationship("Ticket", uselist=False, backref="incident", cascade="all, delete-orphan")
    workflow_instances = relationship(
        "WorkflowInstance", backref="incident", cascade="all, delete-orphan"
    )

    duplicate_id = Column(Integer, ForeignKey("incident.id"))
    duplicates = relationship(
        "Incident", remote_side=[id], lazy="joined", join_depth=2, uselist=True
    )

    commander_id = Column(Integer, ForeignKey("participant.id"))
    commander = relationship(
        "Participant", foreign_keys=[commander_id], lazy="subquery", post_update=True
    )

    reporter_id = Column(Integer, ForeignKey("participant.id"))
    reporter = relationship(
        "Participant", foreign_keys=[reporter_id], lazy="subquery", post_update=True
    )

    liaison_id = Column(Integer, ForeignKey("participant.id"))
    liaison = relationship("Participant", foreign_keys=[liaison_id], post_update=True)

    scribe_id = Column(Integer, ForeignKey("participant.id"))
    scribe = relationship("Participant", foreign_keys=[scribe_id], post_update=True)

    incident_document_id = Column(Integer, ForeignKey("document.id"))
    incident_document = relationship("Document", foreign_keys=[incident_document_id])

    incident_review_document_id = Column(Integer, ForeignKey("document.id"))
    incident_review_document = relationship("Document", foreign_keys=[incident_review_document_id])

    tactical_group_id = Column(Integer, ForeignKey("group.id"))
    tactical_group = relationship("Group", foreign_keys=[tactical_group_id])

    notifications_group_id = Column(Integer, ForeignKey("group.id"))
    notifications_group = relationship("Group", foreign_keys=[notifications_group_id])

    @hybrid_property
    def total_cost(self):
        total_cost = 0
        if self.incident_costs:
            for cost in self.incident_costs:
                total_cost += cost.amount
        return total_cost

    @observes("participants")
    def participant_observer(self, participants):
        self.participants_team = Counter(p.team for p in participants).most_common(1)[0][0]
        self.participants_location = Counter(p.location for p in participants).most_common(1)[0][0]


class ProjectRead(DispatchBase):
    id: Optional[PrimaryKey]
    name: NameStr
    color: Optional[str]
    stable_priority: Optional[IncidentPriorityRead] = None
    allow_self_join: Optional[bool] = Field(True, nullable=True)


class CaseRead(DispatchBase):
    id: PrimaryKey
    name: Optional[NameStr]


class TaskRead(DispatchBase):
    id: PrimaryKey
    assignees: List[Optional[ParticipantRead]] = []
    created_at: Optional[datetime]
    description: Optional[str] = Field(None, nullable=True)
    status: TaskStatus = TaskStatus.open
    weblink: Optional[AnyHttpUrl] = Field(None, nullable=True)


class TaskReadMinimal(DispatchBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)
    status: TaskStatus = TaskStatus.open


# Pydantic models...
class IncidentBase(DispatchBase):
    title: str
    description: str
    resolution: Optional[str]
    status: Optional[IncidentStatus]
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


class IncidentCreate(IncidentBase):
    commander: Optional[ParticipantUpdate]
    commander_email: Optional[str]
    incident_priority: Optional[IncidentPriorityCreate]
    incident_severity: Optional[IncidentSeverityCreate]
    incident_type: Optional[IncidentTypeCreate]
    project: Optional[ProjectRead]
    reporter: Optional[ParticipantUpdate]
    tags: Optional[List[TagRead]] = []


IncidentReadMinimal = ForwardRef("IncidentReadMinimal")


class IncidentReadMinimal(IncidentBase):
    id: PrimaryKey
    closed_at: Optional[datetime] = None
    commander: Optional[ParticipantReadMinimal]
    commanders_location: Optional[str]
    created_at: Optional[datetime] = None
    duplicates: Optional[List[IncidentReadMinimal]] = []
    incident_costs: Optional[List[IncidentCostRead]] = []
    incident_document: Optional[DocumentRead] = None
    incident_priority: IncidentPriorityReadMinimal
    incident_review_document: Optional[DocumentRead] = None
    incident_severity: IncidentSeverityReadMinimal
    incident_type: IncidentTypeReadMinimal
    name: Optional[NameStr]
    participants_location: Optional[str]
    participants_team: Optional[str]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    reporter: Optional[ParticipantReadMinimal]
    reporters_location: Optional[str]
    stable_at: Optional[datetime] = None
    storage: Optional[StorageRead] = None
    tags: Optional[List[TagRead]] = []
    tasks: Optional[List[TaskReadMinimal]] = []
    total_cost: Optional[float]


IncidentReadMinimal.update_forward_refs()


class IncidentUpdate(IncidentBase):
    cases: Optional[List[CaseRead]] = []
    commander: Optional[ParticipantUpdate]
    delay_executive_report_reminder: Optional[datetime] = None
    delay_tactical_report_reminder: Optional[datetime] = None
    duplicates: Optional[List[IncidentReadMinimal]] = []
    incident_costs: Optional[List[IncidentCostUpdate]] = []
    incident_priority: IncidentPriorityBase
    incident_severity: IncidentSeverityBase
    incident_type: IncidentTypeBase
    reported_at: Optional[datetime] = None
    reporter: Optional[ParticipantUpdate]
    stable_at: Optional[datetime] = None
    tags: Optional[List[TagRead]] = []
    terms: Optional[List[TermRead]] = []

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


class IncidentRead(IncidentBase):
    id: PrimaryKey
    cases: Optional[List[CaseRead]] = []
    closed_at: Optional[datetime] = None
    commander: Optional[ParticipantRead]
    commanders_location: Optional[str]
    conference: Optional[ConferenceRead] = None
    conversation: Optional[ConversationRead] = None
    created_at: Optional[datetime] = None
    delay_executive_report_reminder: Optional[datetime] = None
    delay_tactical_report_reminder: Optional[datetime] = None
    documents: Optional[List[DocumentRead]] = []
    duplicates: Optional[List[IncidentReadMinimal]] = []
    events: Optional[List[EventRead]] = []
    incident_costs: Optional[List[IncidentCostRead]] = []
    incident_priority: IncidentPriorityRead
    incident_severity: IncidentSeverityRead
    incident_type: IncidentTypeRead
    last_executive_report: Optional[ReportRead]
    last_tactical_report: Optional[ReportRead]
    name: Optional[NameStr]
    participants: Optional[List[ParticipantRead]] = []
    participants_location: Optional[str]
    participants_team: Optional[str]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    reporter: Optional[ParticipantRead]
    reporters_location: Optional[str]
    stable_at: Optional[datetime] = None
    storage: Optional[StorageRead] = None
    tags: Optional[List[TagRead]] = []
    tasks: Optional[List[TaskRead]] = []
    terms: Optional[List[TermRead]] = []
    ticket: Optional[TicketRead] = None
    total_cost: Optional[float]
    workflow_instances: Optional[List[WorkflowInstanceRead]] = []


class IncidentExpandedPagination(Pagination):
    itemsPerPage: int
    page: int
    items: List[IncidentRead] = []


class IncidentPagination(Pagination):
    items: List[IncidentReadMinimal] = []
