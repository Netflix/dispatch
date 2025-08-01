"""Models and schemas for the Dispatch case management system."""

from collections import Counter, defaultdict
from datetime import datetime
from typing import Any
from pydantic import field_validator, Field
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType, observes

from dispatch.case.enums import CostModelType
from dispatch.case_cost.models import CaseCostReadMinimal
from dispatch.case.priority.models import CasePriorityBase, CasePriorityCreate, CasePriorityRead
from dispatch.case.severity.models import CaseSeverityBase, CaseSeverityCreate, CaseSeverityRead
from dispatch.case.type.models import CaseTypeBase, CaseTypeCreate, CaseTypeRead
from dispatch.case_cost.models import (
    CaseCostRead,
    CaseCostUpdate,
)
from dispatch.conversation.models import ConversationRead
from dispatch.database.core import Base
from dispatch.document.models import Document, DocumentRead
from dispatch.entity.models import EntityRead
from dispatch.enums import Visibility
from dispatch.event.models import EventRead
from dispatch.group.models import Group, GroupRead
from dispatch.individual.models import IndividualContactRead
from dispatch.messaging.strings import CASE_RESOLUTION_DEFAULT
from dispatch.models import (
    DispatchBase,
    NameStr,
    Pagination,
    PrimaryKey,
    ProjectMixin,
    TimeStampMixin,
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
    """SQLAlchemy model for a Case, representing an incident or issue in the system."""

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
    genai_analysis = Column(JSONB, default={}, nullable=False, server_default="{}")
    event = Column(Boolean, default=False)
    stable_at = Column(DateTime)

    search_vector = Column(
        TSVectorType(
            "name", "title", "description", weights={"name": "A", "title": "B", "description": "C"}
        )
    )

    # relationships
    assignee_id = Column(Integer, ForeignKey("participant.id", ondelete="CASCADE"))
    assignee = relationship(Participant, foreign_keys=[assignee_id], post_update=True)

    reporter_id = Column(Integer, ForeignKey("participant.id", ondelete="CASCADE"))
    reporter = relationship(Participant, foreign_keys=[reporter_id], post_update=True)

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

    feedback = relationship("Feedback", backref="case", cascade="all, delete-orphan")

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

    case_notes = relationship(
        "CaseNotes",
        back_populates="case",
        cascade="all, delete-orphan",
        uselist=False,
    )

    @observes("participants")
    def participant_observer(self, participants):
        """Update team and location fields based on the most common values among participants."""
        self.participants_team = Counter(p.team for p in participants).most_common(1)[0][0]
        self.participants_location = Counter(p.location for p in participants).most_common(1)[0][0]

    @property
    def has_channel(self) -> bool:
        """Return True if the case has a conversation channel but not a thread."""
        if not self.conversation:
            return False
        return True if not self.conversation.thread_id else False

    @property
    def has_thread(self) -> bool:
        """Return True if the case has a conversation thread."""
        if not self.conversation:
            return False
        return True if self.conversation.thread_id else False

    @property
    def participant_emails(self) -> list:
        """Return a list of emails for all participants in the case."""
        return [participant.individual.email for participant in self.participants]

    @hybrid_property
    def total_cost_classic(self):
        """Calculate the total cost for classic cost model types."""
        total_cost = 0
        if self.case_costs:
            for cost in self.case_costs:
                if cost.case_cost_type.model_type == CostModelType.new:
                    continue
                total_cost += cost.amount
        return total_cost

    @hybrid_property
    def total_cost_new(self):
        """Calculate the total cost for new cost model types."""
        total_cost = 0
        if self.case_costs:
            for cost in self.case_costs:
                if cost.case_cost_type.model_type == CostModelType.classic:
                    continue
                total_cost += cost.amount
        return total_cost


class CaseNotes(Base, TimeStampMixin):
    """SQLAlchemy model for case investigation notes."""

    id = Column(Integer, primary_key=True)
    content = Column(String)

    # Foreign key to case
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))
    case = relationship("Case", back_populates="case_notes")

    # Foreign key to individual who last updated
    last_updated_by_id = Column(Integer, ForeignKey("individual_contact.id"))
    last_updated_by = relationship("IndividualContact", foreign_keys=[last_updated_by_id])


class SignalRead(DispatchBase):
    """Pydantic model for reading signal data."""

    id: PrimaryKey
    name: str
    owner: str
    description: str | None = None
    variant: str | None = None
    external_id: str
    external_url: str | None = None
    workflow_instances: list[WorkflowInstanceRead] | None = []
    tags: list[TagRead] | None = []


class SignalInstanceRead(DispatchBase):
    """Pydantic model for reading signal instance data."""

    created_at: datetime
    entities: list[EntityRead] | None = []
    raw: Any
    signal: SignalRead
    tags: list[TagRead] | None = []


class ProjectRead(DispatchBase):
    """Pydantic model for reading project data."""

    id: PrimaryKey | None = None
    name: NameStr
    display_name: str | None = None
    color: str | None = None
    allow_self_join: bool | None = Field(True, nullable=True)


# CaseNotes Pydantic models
class CaseNotesBase(DispatchBase):
    """Base Pydantic model for case notes data."""

    content: str | None = None


class CaseNotesCreate(CaseNotesBase):
    """Pydantic model for creating case notes."""

    pass


class CaseNotesUpdate(CaseNotesBase):
    """Pydantic model for updating case notes."""

    pass


class CaseNotesRead(CaseNotesBase):
    """Pydantic model for reading case notes data."""

    id: PrimaryKey
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_updated_by: IndividualContactRead | None = None


# Pydantic models...
class CaseBase(DispatchBase):
    """Base Pydantic model for case data."""

    title: str
    description: str | None = None
    resolution: str | None = None
    resolution_reason: CaseResolutionReason | None = None
    status: CaseStatus | None = None
    visibility: Visibility | None = None

    @field_validator("title")
    @classmethod
    def title_required(cls, v):
        """Ensure the title field is not empty."""
        if not v:
            raise ValueError("must not be empty string")
        return v

    @field_validator("description")
    @classmethod
    def description_required(cls, v):
        """Ensure the description field is not empty."""
        if not v:
            raise ValueError("must not be empty string")
        return v


class CaseCreate(CaseBase):
    """Pydantic model for creating a new case."""

    assignee: ParticipantUpdate | None = None
    case_priority: CasePriorityCreate | None = None
    case_severity: CaseSeverityCreate | None = None
    case_type: CaseTypeCreate | None = None
    dedicated_channel: bool | None = None
    project: ProjectRead | None = None
    reporter: ParticipantUpdate | None = None
    tags: list[TagRead] | None = []
    event: bool | None = False


class CaseReadBasic(DispatchBase):
    """Pydantic model for reading basic case data."""

    id: PrimaryKey
    name: NameStr | None = None


class IncidentReadBasic(DispatchBase):
    """Pydantic model for reading basic incident data."""

    id: PrimaryKey
    name: NameStr | None = None


class CaseReadMinimal(CaseBase):
    """Pydantic model for reading minimal case data."""

    id: PrimaryKey
    name: NameStr | None = None
    status: CaseStatus | None = None  # Used in table and for action disabling
    closed_at: datetime | None = None
    reported_at: datetime | None = None
    stable_at: datetime | None = None
    dedicated_channel: bool | None = None  # Used by CaseStatus component
    case_type: CaseTypeRead
    case_severity: CaseSeverityRead
    case_priority: CasePriorityRead
    project: ProjectRead
    assignee: ParticipantReadMinimal | None = None
    case_costs: list[CaseCostReadMinimal] = []
    incidents: list[IncidentReadBasic] | None = []


class CaseReadMinimalWithExtras(CaseBase):
    """Pydantic model for reading minimal case data."""

    id: PrimaryKey
    title: str
    name: NameStr | None = None
    description: str | None = None
    resolution: str | None = None
    resolution_reason: CaseResolutionReason | None = None
    visibility: Visibility | None = None
    status: CaseStatus | None = None  # Used in table and for action disabling
    reported_at: datetime | None = None
    triage_at: datetime | None = None
    stable_at: datetime | None = None
    escalated_at: datetime | None = None
    closed_at: datetime | None = None
    dedicated_channel: bool | None = None  # Used by CaseStatus component
    case_type: CaseTypeRead
    case_severity: CaseSeverityRead
    case_priority: CasePriorityRead
    project: ProjectRead
    reporter: ParticipantReadMinimal | None = None
    assignee: ParticipantReadMinimal | None = None
    case_costs: list[CaseCostReadMinimal] = []
    participants: list[ParticipantReadMinimal] = []
    tags: list[TagRead] = []
    ticket: TicketRead | None = None


CaseReadMinimal.update_forward_refs()


class CaseRead(CaseBase):
    """Pydantic model for reading detailed case data."""

    id: PrimaryKey
    assignee: ParticipantRead | None = None
    case_costs: list[CaseCostRead] = []
    case_priority: CasePriorityRead
    case_severity: CaseSeverityRead
    case_type: CaseTypeRead
    closed_at: datetime | None = None
    conversation: ConversationRead | None = None
    created_at: datetime | None = None
    stable_at: datetime | None = None
    documents: list[DocumentRead] | None = []
    duplicates: list[CaseReadBasic] | None = []
    escalated_at: datetime | None = None
    events: list[EventRead] | None = []
    genai_analysis: dict[str, Any] | None = {}
    groups: list[GroupRead] | None = []
    incidents: list[IncidentReadBasic] | None = []
    name: NameStr | None
    participants: list[ParticipantRead] | None = []
    project: ProjectRead
    related: list[CaseReadMinimal] | None = []
    reported_at: datetime | None = None
    reporter: ParticipantRead | None = None
    signal_instances: list[SignalInstanceRead] | None = []
    storage: StorageRead | None = None
    tags: list[TagRead] | None = []
    ticket: TicketRead | None = None
    total_cost_classic: float | None
    total_cost_new: float | None
    triage_at: datetime | None = None
    updated_at: datetime | None = None
    workflow_instances: list[WorkflowInstanceRead] | None = []
    event: bool | None = False
    case_notes: CaseNotesRead | None = None


class CaseUpdate(CaseBase):
    """Pydantic model for updating case data."""

    assignee: ParticipantUpdate | None = None
    case_costs: list[CaseCostUpdate] = []
    case_priority: CasePriorityBase | None = None
    case_severity: CaseSeverityBase | None = None
    case_type: CaseTypeBase | None = None
    closed_at: datetime | None = None
    stable_at: datetime | None = None
    duplicates: list[CaseReadBasic] | None = []
    related: list[CaseRead] | None = []
    reporter: ParticipantUpdate | None = None
    escalated_at: datetime | None = None
    incidents: list[IncidentReadBasic] | None = []
    reported_at: datetime | None = None
    tags: list[TagRead] | None = []
    triage_at: datetime | None = None
    case_notes: CaseNotesUpdate | None = None

    @field_validator("tags")
    @classmethod
    def find_exclusive(cls, tags: list[TagRead] | None) -> list[TagRead] | None:
        """Ensure only one exclusive tag per tag type is present."""
        if not tags:
            return tags

        # Group tags by tag_type.id
        exclusive_tags = defaultdict(list)
        for t in tags:
            if t.tag_type and t.tag_type.exclusive:
                exclusive_tags[t.tag_type.id].append(t)

            # Check for multiple exclusive tags of the same type
            for tag_list in exclusive_tags.values():
                if len(tag_list) > 1:
                    raise ValueError(
                        "Found multiple exclusive tags. Please ensure that only one tag of a given "
                        f"type is applied. Tags: {','.join([t.name for t in tag_list])}"
                    )

        return tags


class CasePagination(Pagination):
    """Pydantic model for paginated minimal case results."""

    items: list[CaseReadMinimal] = []


class CasePaginationMinimalWithExtras(Pagination):
    """Pydantic model for paginated minimal case results."""

    items: list[CaseReadMinimalWithExtras] = []


class CaseExpandedPagination(Pagination):
    """Pydantic model for paginated expanded case results."""

    items: list[CaseRead] = []
