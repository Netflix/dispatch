from datetime import datetime
from collections import Counter
from typing import List, Optional, Any

from pydantic import validator
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    select,
    join,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from fastapi_permissions import Allow

from dispatch.config import (
    INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT,
    INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT,
    INCIDENT_RESOURCE_NOTIFICATIONS_GROUP,
    INCIDENT_RESOURCE_TACTICAL_GROUP,
)
from dispatch.enums import UserRoles
from dispatch.conference.models import ConferenceRead
from dispatch.conversation.models import ConversationRead
from dispatch.database import Base
from dispatch.document.models import DocumentRead
from dispatch.enums import Visibility
from dispatch.event.models import EventRead
from dispatch.incident_priority.models import (
    IncidentPriorityBase,
    IncidentPriorityCreate,
    IncidentPriorityRead,
)
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead, IncidentTypeBase
from dispatch.individual.models import IndividualContact
from dispatch.models import DispatchBase, IndividualReadNested, TimeStampMixin
from dispatch.participant.models import Participant, ParticipantRead
from dispatch.participant_role.models import ParticipantRole, ParticipantRoleType
from dispatch.report.enums import ReportTypes
from dispatch.report.models import ReportRead
from dispatch.storage.models import StorageRead
from dispatch.tag.models import TagRead
from dispatch.ticket.models import TicketRead
from dispatch.workflow.models import WorkflowInstanceRead

from .enums import IncidentStatus


assoc_incident_terms = Table(
    "assoc_incident_terms",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("term_id", Integer, ForeignKey("term.id")),
    PrimaryKeyConstraint("incident_id", "term_id"),
)

assoc_incident_tags = Table(
    "assoc_incident_tags",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
    PrimaryKeyConstraint("incident_id", "tag_id"),
)


class Incident(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default=IncidentStatus.active)
    cost = Column(Float, default=0)
    visibility = Column(String, default=Visibility.open)

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
    def commander(self):
        if self.participants:
            for p in self.participants:
                for pr in p.participant_roles:
                    if (
                        pr.role == ParticipantRoleType.incident_commander
                        and pr.renounced_at
                        is None  # Column renounced_at will be null for the current incident commander
                    ):
                        return p.individual

    @commander.expression
    def commander(cls):
        return (
            select([IndividualContact])
            .where(Participant.incident_id == cls.id)
            .where(ParticipantRole.role == ParticipantRoleType.incident_commander)
            .where(ParticipantRole.renounced_at == None)  # noqa
        )

    @hybrid_property
    def reporter(self):
        if self.participants:
            for p in self.participants:
                for role in p.participant_roles:
                    if role.role == ParticipantRoleType.reporter:
                        return p.individual

    @reporter.expression
    def reporter(cls):
        return (
            select([IndividualContact])
            .where(Participant.incident_id == cls.id)
            .where(ParticipantRole.role == ParticipantRoleType.reporter)
            .where(ParticipantRole.renounced_at == None)  # noqa
        )

    @hybrid_property
    def tactical_group(self):
        if self.groups:
            for g in self.groups:
                if g.resource_type == INCIDENT_RESOURCE_TACTICAL_GROUP:
                    return g

    @hybrid_property
    def notifications_group(self):
        if self.groups:
            for g in self.groups:
                if g.resource_type == INCIDENT_RESOURCE_NOTIFICATIONS_GROUP:
                    return g

    @hybrid_property
    def incident_document(self):
        if self.documents:
            for d in self.documents:
                if d.resource_type == INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT:
                    return d

    @hybrid_property
    def incident_review_document(self):
        if self.documents:
            for d in self.documents:
                if d.resource_type == INCIDENT_RESOURCE_INCIDENT_REVIEW_DOCUMENT:
                    return d

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

    @hybrid_property
    def primary_team(self):
        if self.participants:
            teams = [p.team for p in self.participants]
            return Counter(teams).most_common(1)[0][0]

    @hybrid_property
    def primary_location(self):
        if self.participants:
            locations = [p.location for p in self.participants]
            return Counter(locations).most_common(1)[0][0]

    # resources
    conference = relationship("Conference", uselist=False, backref="incident")
    conversation = relationship("Conversation", uselist=False, backref="incident")
    documents = relationship("Document", lazy="subquery", backref="incident")
    events = relationship("Event", backref="incident")
    feedback = relationship("Feedback", backref="incident")
    groups = relationship("Group", lazy="subquery", backref="incident")
    incident_priority = relationship("IncidentPriority", backref="incident")
    incident_priority_id = Column(Integer, ForeignKey("incident_priority.id"))
    incident_type = relationship("IncidentType", backref="incident")
    incident_type_id = Column(Integer, ForeignKey("incident_type.id"))
    participants = relationship("Participant", backref="incident")
    reports = relationship("Report", backref="incident")
    storage = relationship("Storage", uselist=False, backref="incident")
    tags = relationship("Tag", secondary=assoc_incident_tags, backref="incidents")
    tasks = relationship("Task", backref="incident")
    terms = relationship("Term", secondary=assoc_incident_terms, backref="incidents")
    ticket = relationship("Ticket", uselist=False, backref="incident")
    workflow_instances = relationship("WorkflowInstance", backref="incident")

    # allow incidents to be marked as duplicate
    duplicate_id = Column(Integer, ForeignKey("incident.id"))
    duplicates = relationship("Incident", remote_side=[id], uselist=True)


# Pydantic models...
class IncidentBase(DispatchBase):
    title: str
    description: str
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
    id: int
    cost: float = None
    name: str = None
    reporter: Optional[IndividualReadNested]
    commander: Optional[IndividualReadNested]
    incident_priority: IncidentPriorityRead
    incident_type: IncidentTypeRead
    created_at: Optional[datetime] = None
    reported_at: Optional[datetime] = None
    stable_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class IncidentCreate(IncidentBase):
    incident_priority: Optional[IncidentPriorityCreate]
    incident_type: Optional[IncidentTypeCreate]
    tags: Optional[List[Any]] = []  # any until we figure out circular imports


class IncidentUpdate(IncidentBase):
    incident_priority: IncidentPriorityBase
    incident_type: IncidentTypeBase
    reported_at: Optional[datetime] = None
    stable_at: Optional[datetime] = None
    commander: Optional[IndividualReadNested]
    reporter: Optional[IndividualReadNested]
    duplicates: Optional[List[IncidentReadNested]] = []
    tags: Optional[List[Any]] = []  # any until we figure out circular imports
    terms: Optional[List[Any]] = []  # any until we figure out circular imports


class IncidentRead(IncidentBase):
    id: int
    cost: float = None
    name: str = None
    primary_team: Any
    primary_location: Any
    reporter: Optional[IndividualReadNested]
    commander: Optional[IndividualReadNested]
    last_tactical_report: Optional[ReportRead]
    last_executive_report: Optional[ReportRead]
    incident_priority: IncidentPriorityRead
    incident_type: IncidentTypeRead
    participants: Optional[List[ParticipantRead]] = []
    workflow_instances: Optional[List[WorkflowInstanceRead]] = []
    storage: Optional[StorageRead] = None
    ticket: Optional[TicketRead] = None
    documents: Optional[List[DocumentRead]] = []
    tags: Optional[List[TagRead]] = []
    terms: Optional[List[Any]] = []  # any until we figure out circular imports
    conference: Optional[ConferenceRead] = None
    conversation: Optional[ConversationRead] = None
    events: Optional[List[EventRead]] = []
    created_at: Optional[datetime] = None
    reported_at: Optional[datetime] = None
    duplicates: Optional[List[IncidentReadNested]] = []
    stable_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    def __acl__(self):
        if self.visibility == Visibility.restricted:
            return [
                (Allow, f"role:{UserRoles.admin}", "view"),
                (Allow, f"role:{UserRoles.admin}", "edit"),
            ]
        return [
            (Allow, f"role:{UserRoles.user}", "view"),
            (Allow, f"role:{UserRoles.user}", "edit"),
        ]


class IncidentPagination(DispatchBase):
    total: int
    items: List[IncidentRead] = []
