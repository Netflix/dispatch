from datetime import datetime
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
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from fastapi_permissions import Allow

from dispatch.config import INCIDENT_RESOURCE_FAQ_DOCUMENT, INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT

from dispatch.auth.models import UserRoles
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
from dispatch.participant.models import ParticipantRead
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.storage.models import StorageRead
from dispatch.ticket.models import TicketRead
from dispatch.models import DispatchBase, IndividualReadNested, TimeStampMixin

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

    # NOTE these only work in python, if want them to be executed via sql we need to
    # write the coresponding expressions. See:
    # https://docs.sqlalchemy.org/en/13/orm/extensions/hybrid.html
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

    @hybrid_property
    def reporter(self):
        if self.participants:
            for p in self.participants:
                for role in p.participant_roles:
                    if role.role == ParticipantRoleType.reporter:
                        return p.individual

    @hybrid_property
    def incident_document(self):
        if self.documents:
            for d in self.documents:
                if d.resource_type == INCIDENT_RESOURCE_INVESTIGATION_DOCUMENT:
                    return d

    @hybrid_property
    def incident_faq(self):
        if self.documents:
            for d in self.documents:
                if d.resource_type == INCIDENT_RESOURCE_FAQ_DOCUMENT:
                    return d

    @hybrid_property
    def last_status_report(self):
        if self.status_reports:
            return sorted(self.status_reports, key=lambda r: r.created_at)[-1]

    # resources
    conference = relationship("Conference", uselist=False, backref="incident")
    conversation = relationship("Conversation", uselist=False, backref="incident")
    documents = relationship("Document", lazy="subquery", backref="incident")
    events = relationship("Event", backref="incident")
    groups = relationship("Group", lazy="subquery", backref="incident")
    incident_priority = relationship("IncidentPriority", backref="incident")
    incident_priority_id = Column(Integer, ForeignKey("incident_priority.id"))
    incident_type = relationship("IncidentType", backref="incident")
    incident_type_id = Column(Integer, ForeignKey("incident_type.id"))
    participants = relationship("Participant", backref="incident")
    status_reports = relationship("StatusReport", backref="incident")
    storage = relationship("Storage", uselist=False, backref="incident")
    tags = relationship("Tag", secondary=assoc_incident_tags, backref="incidents")
    tasks = relationship("Task", backref="incident")
    terms = relationship("Term", secondary=assoc_incident_terms, backref="incidents")
    ticket = relationship("Ticket", uselist=False, backref="incident")


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


class IncidentCreate(IncidentBase):
    incident_priority: IncidentPriorityCreate
    incident_type: IncidentTypeCreate


class IncidentUpdate(IncidentBase):
    incident_priority: IncidentPriorityBase
    incident_type: IncidentTypeBase
    reported_at: Optional[datetime] = None
    stable_at: Optional[datetime] = None
    commander: Optional[IndividualReadNested]
    reporter: Optional[IndividualReadNested]
    tags: Optional[List[Any]] = []  # any until we figure out circular imports
    terms: Optional[List[Any]] = []  # any until we figure out circular imports


class IncidentRead(IncidentBase):
    id: int
    cost: float = None
    name: str = None
    reporter: Optional[IndividualReadNested]
    commander: Optional[IndividualReadNested]
    last_status_report: Optional[Any]
    incident_priority: IncidentPriorityRead
    incident_type: IncidentTypeRead
    participants: Optional[List[ParticipantRead]] = []
    storage: Optional[StorageRead] = None
    ticket: Optional[TicketRead] = None
    documents: Optional[List[DocumentRead]] = []
    tags: Optional[List[Any]] = []  # any until we figure out circular imports
    terms: Optional[List[Any]] = []  # any until we figure out circular imports
    conference: Optional[ConferenceRead] = None
    conversation: Optional[ConversationRead] = None
    events: Optional[List[EventRead]] = []

    created_at: Optional[datetime] = None
    reported_at: Optional[datetime] = None
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
