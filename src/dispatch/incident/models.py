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

from dispatch.conference.models import ConferenceRead
from dispatch.conversation.models import ConversationRead
from dispatch.database.core import Base
from dispatch.document.models import DocumentRead
from dispatch.enums import Visibility
from dispatch.event.models import EventRead
from dispatch.incident_cost.models import IncidentCostRead, IncidentCostUpdate
from dispatch.incident_priority.models import (
    IncidentPriorityBase,
    IncidentPriorityCreate,
    IncidentPriorityRead,
)
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead, IncidentTypeBase
from dispatch.models import DispatchBase, ProjectMixin, TimeStampMixin
from dispatch.participant.models import ParticipantRead, ParticipantUpdate
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.report.enums import ReportTypes
from dispatch.document.models import Document
from dispatch.group.models import Group
from dispatch.participant.models import Participant
from dispatch.report.models import ReportRead
from dispatch.storage.models import StorageRead
from dispatch.tag.models import TagRead
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
    resolution = Column(String)
    status = Column(String, default=IncidentStatus.active)
    visibility = Column(String, default=Visibility.open, nullable=False)
    participants_team = Column(String)
    participants_location = Column(String)
    commanders_location = Column(String)
    reporters_location = Column(String)

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
        order_by="IncidentCost.created_at",
    )

    incident_priority = relationship("IncidentPriority", backref="incident")
    incident_priority_id = Column(Integer, ForeignKey("incident_priority.id"))

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
        backref="incidents",
    )
    tasks = relationship("Task", backref="incident", cascade="all, delete-orphan")
    terms = relationship("Term", secondary=assoc_incident_terms, backref="incidents")
    ticket = relationship("Ticket", uselist=False, backref="incident", cascade="all, delete-orphan")
    workflow_instances = relationship(
        "WorkflowInstance", backref="incident", cascade="all, delete-orphan"
    )

    duplicate_id = Column(Integer, ForeignKey("incident.id"))
    duplicates = relationship("Incident", remote_side=[id], uselist=True)

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

    @hybrid_property
    def total_cost(self):
        if self.incident_costs:
            total_cost = 0
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


# Pydantic models...
class IncidentBase(DispatchBase):
    title: str
    description: str
    resolution: Optional[str]
    status: Optional[IncidentStatus] = IncidentStatus.active
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


class IncidentReadNested(IncidentBase):
    id: PrimaryKey
    closed_at: Optional[datetime] = None
    commander: Optional[ParticipantRead]
    created_at: Optional[datetime] = None
    incident_priority: IncidentPriorityRead
    incident_type: IncidentTypeRead
    name: Optional[NameStr]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    reporter: Optional[ParticipantRead]
    stable_at: Optional[datetime] = None


class IncidentCreate(IncidentBase):
    commander: Optional[ParticipantUpdate]
    incident_priority: Optional[IncidentPriorityCreate]
    incident_type: Optional[IncidentTypeCreate]
    project: ProjectRead
    reporter: Optional[ParticipantUpdate]
    tags: Optional[List[TagRead]] = []


class IncidentUpdate(IncidentBase):
    commander: Optional[ParticipantUpdate]
    duplicates: Optional[List[IncidentReadNested]] = []
    incident_costs: Optional[List[IncidentCostUpdate]] = []
    incident_priority: IncidentPriorityBase
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
            for t in v:
                if t.tag_type.exclusive:
                    exclusive_tags[t.tag_type.id].append(t)

            for v in exclusive_tags.values():
                if len(v) > 1:
                    raise ValueError(
                        f"Found multiple exclusive tags. Please ensure that only one tag of a given type is applied. Tags: {','.join([t.name for t in v])}"
                    )
        return v


class IncidentReadMinimal(IncidentBase):
    id: PrimaryKey
    closed_at: Optional[datetime] = None
    commander: Optional[ParticipantRead]
    commanders_location: Optional[str]
    created_at: Optional[datetime] = None
    duplicates: Optional[List[IncidentReadNested]] = []
    incident_costs: Optional[List[IncidentCostRead]] = []
    incident_priority: IncidentPriorityRead
    incident_type: IncidentTypeRead
    name: Optional[NameStr]
    participants_location: Optional[str]
    participants_team: Optional[str]
    project: ProjectRead
    reported_at: Optional[datetime] = None
    reporter: Optional[ParticipantRead]
    reporters_location: Optional[str]
    stable_at: Optional[datetime] = None
    tags: Optional[List[TagRead]] = []
    total_cost: Optional[float]


class IncidentRead(IncidentReadMinimal):
    conference: Optional[ConferenceRead] = None
    conversation: Optional[ConversationRead] = None
    documents: Optional[List[DocumentRead]] = []
    events: Optional[List[EventRead]] = []
    last_executive_report: Optional[ReportRead]
    last_tactical_report: Optional[ReportRead]
    participants: Optional[List[ParticipantRead]] = []
    storage: Optional[StorageRead] = None
    terms: Optional[List[TermRead]] = []
    ticket: Optional[TicketRead] = None
    workflow_instances: Optional[List[WorkflowInstanceRead]] = []


class IncidentPagination(DispatchBase):
    total: int
    itemsPerPage: int
    page: int
    items: List[IncidentRead] = []
