"""Models for incident resources in the Dispatch application."""

from collections import Counter, defaultdict
from datetime import datetime

from pydantic import field_validator, AnyHttpUrl

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
    commander = relationship("Participant", foreign_keys=[commander_id], post_update=True)

    reporter_id = Column(Integer, ForeignKey("participant.id"))
    reporter = relationship("Participant", foreign_keys=[reporter_id], post_update=True)

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

    summary = Column(String, nullable=True)

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
    """Pydantic model for reading a project resource."""

    id: PrimaryKey | None = None
    name: NameStr
    color: str | None = None
    stable_priority: IncidentPriorityRead | None = None
    allow_self_join: bool | None = True
    display_name: str | None = None


class CaseRead(DispatchBase):
    """Pydantic model for reading a case resource."""

    id: PrimaryKey
    name: NameStr | None = None


class TaskRead(DispatchBase):
    """Pydantic model for reading a task resource."""

    id: PrimaryKey
    assignees: list[ParticipantRead | None] = []
    created_at: datetime | None = None
    description: str | None = None
    status: TaskStatus = TaskStatus.open
    owner: ParticipantRead | None = None
    weblink: AnyHttpUrl | None = None
    resolve_by: datetime | None = None
    resolved_at: datetime | None = None
    ticket: TicketRead | None = None


class TaskReadMinimal(DispatchBase):
    """Pydantic model for reading a minimal task resource."""

    id: PrimaryKey
    description: str | None = None
    status: TaskStatus = TaskStatus.open


# Pydantic models...
class IncidentBase(DispatchBase):
    """Base Pydantic model for incident resources."""

    title: str
    description: str
    resolution: str | None = None
    status: IncidentStatus | None = None
    visibility: Visibility | None = None

    @field_validator("title")
    @classmethod
    def title_required(cls, v: str) -> str:
        """Ensures the title is not an empty string."""
        if not v:
            raise ValueError("must not be empty string")
        return v

    @field_validator("description")
    @classmethod
    def description_required(cls, v: str) -> str:
        """Ensures the description is not an empty string."""
        if not v:
            raise ValueError("must not be empty string")
        return v


class IncidentCreate(IncidentBase):
    """Pydantic model for creating an incident resource."""

    commander: ParticipantUpdate | None = None
    commander_email: str | None = None
    incident_priority: IncidentPriorityCreate | None = None
    incident_severity: IncidentSeverityCreate | None = None
    incident_type: IncidentTypeCreate | None = None
    project: ProjectRead | None = None
    reporter: ParticipantUpdate | None = None
    tags: list[TagRead] | None = []


class IncidentReadBasic(DispatchBase):
    """Pydantic model for reading a basic incident resource."""

    id: PrimaryKey
    name: NameStr | None = None


class IncidentReadMinimal(IncidentBase):
    """Pydantic model for reading a minimal incident resource."""

    id: PrimaryKey
    closed_at: datetime | None = None
    commander: ParticipantReadMinimal | None = None
    commanders_location: str | None = None
    created_at: datetime | None = None
    duplicates: list[IncidentReadBasic] | None = []
    incident_costs: list[IncidentCostRead] | None = []
    incident_document: DocumentRead | None = None
    incident_priority: IncidentPriorityReadMinimal
    incident_review_document: DocumentRead | None = None
    incident_severity: IncidentSeverityReadMinimal
    incident_type: IncidentTypeReadMinimal
    name: NameStr | None = None
    participants_location: str | None = None
    participants_team: str | None = None
    project: ProjectRead
    reported_at: datetime | None = None
    reporter: ParticipantReadMinimal | None = None
    reporters_location: str | None = None
    stable_at: datetime | None = None
    storage: StorageRead | None = None
    summary: str | None = None
    tags: list[TagRead] | None = []
    tasks: list[TaskReadMinimal] | None = []
    total_cost: float | None = None


class IncidentUpdate(IncidentBase):
    """Pydantic model for updating an incident resource."""

    cases: list[CaseRead] | None = []
    commander: ParticipantUpdate | None = None
    delay_executive_report_reminder: datetime | None = None
    delay_tactical_report_reminder: datetime | None = None
    duplicates: list[IncidentReadBasic] | None = []
    incident_costs: list[IncidentCostUpdate] | None = []
    incident_priority: IncidentPriorityBase
    incident_severity: IncidentSeverityBase
    incident_type: IncidentTypeBase
    reported_at: datetime | None = None
    reporter: ParticipantUpdate | None = None
    stable_at: datetime | None = None
    summary: str | None = None
    tags: list[TagRead] | None = []
    terms: list[TermRead] | None = []

    @field_validator("tags")
    @classmethod
    def find_exclusive(cls, v):
        """Ensures only one exclusive tag per tag type is applied."""
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
    """Pydantic model for reading an incident resource."""

    id: PrimaryKey
    cases: list[CaseRead] | None = []
    closed_at: datetime | None = None
    commander: ParticipantRead | None = None
    commanders_location: str | None = None
    conference: ConferenceRead | None = None
    conversation: ConversationRead | None = None
    created_at: datetime | None = None
    delay_executive_report_reminder: datetime | None = None
    delay_tactical_report_reminder: datetime | None = None
    documents: list[DocumentRead] | None = []
    duplicates: list[IncidentReadBasic] | None = []
    events: list[EventRead] | None = []
    incident_costs: list[IncidentCostRead] | None = []
    incident_priority: IncidentPriorityRead
    incident_severity: IncidentSeverityRead
    incident_type: IncidentTypeRead
    last_executive_report: ReportRead | None = None
    last_tactical_report: ReportRead | None = None
    name: NameStr | None = None
    participants: list[ParticipantRead] | None = []
    participants_location: str | None = None
    participants_team: str | None = None
    project: ProjectRead
    reported_at: datetime | None = None
    reporter: ParticipantRead | None = None
    reporters_location: str | None = None
    stable_at: datetime | None = None
    storage: StorageRead | None = None
    summary: str | None = None
    tags: list[TagRead] | None = []
    tasks: list[TaskRead] | None = []
    terms: list[TermRead] | None = []
    ticket: TicketRead | None = None
    total_cost: float | None = None
    workflow_instances: list[WorkflowInstanceRead] | None = []


class IncidentExpandedPagination(Pagination):
    """Pydantic model for paginated expanded incident results."""

    itemsPerPage: int
    page: int
    items: list[IncidentRead] = []


class IncidentPagination(Pagination):
    """Pydantic model for paginated incident results."""

    items: list[IncidentReadMinimal] = []
