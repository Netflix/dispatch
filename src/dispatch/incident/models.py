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

from dispatch.conversation.models import ConversationRead
from dispatch.database import Base
from dispatch.document.models import DocumentRead
from dispatch.enums import Visibility
from dispatch.incident_priority.models import (
    IncidentPriorityCreate,
    IncidentPriorityRead,
    IncidentPriorityBase,
)
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead, IncidentTypeBase
from dispatch.models import DispatchBase, IndividualReadNested, TimeStampMixin
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.storage.models import StorageRead
from dispatch.ticket.models import TicketRead

from .enums import IncidentStatus

assoc_incident_terms = Table(
    "assoc_incident_terms",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("term_id", Integer, ForeignKey("term.id")),
    PrimaryKeyConstraint("incident_id", "term_id"),
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
                for pr in p.participant_role:
                    if (
                        pr.role == ParticipantRoleType.incident_commander
                        and pr.renounce_at
                        is None  # Column renounce_at will be null for the current incident commander
                    ):
                        return p.individual

    @hybrid_property
    def reporter(self):
        if self.participants:
            for p in self.participants:
                for role in p.participant_role:
                    if role.role == ParticipantRoleType.reporter:
                        return p.individual

    @hybrid_property
    def last_status_report(self):
        if self.status_reports:
            return sorted(self.status_reports, key=lambda r: r.created_at)[-1]

    # resources
    groups = relationship("Group", lazy="subquery", backref="incident")
    conversation = relationship("Conversation", uselist=False, backref="incident")
    storage = relationship("Storage", uselist=False, backref="incident")
    ticket = relationship("Ticket", uselist=False, backref="incident")
    documents = relationship("Document", lazy="subquery", backref="incident")
    participants = relationship("Participant", backref="incident")
    incident_type_id = Column(Integer, ForeignKey("incident_type.id"))
    incident_type = relationship("IncidentType", backref="incident")
    incident_priority_id = Column(Integer, ForeignKey("incident_priority.id"))
    incident_priority = relationship("IncidentPriority", backref="incident")
    status_reports = relationship("StatusReport", backref="incident")
    tasks = relationship("Task", backref="incident")
    terms = relationship("Term", secondary=assoc_incident_terms, backref="incidents")


# Pydantic models...
class IncidentBase(DispatchBase):
    title: str
    description: str
    status: Optional[IncidentStatus] = IncidentStatus.active

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
    visibility: Visibility
    incident_priority: IncidentPriorityBase
    incident_type: IncidentTypeBase
    reported_at: Optional[datetime] = None
    stable_at: Optional[datetime] = None
    commander: Optional[IndividualReadNested]
    reporter: Optional[IndividualReadNested]


class IncidentRead(IncidentBase):
    id: int
    cost: float = None
    name: str = None
    reporter: Optional[IndividualReadNested]
    commander: Optional[IndividualReadNested]
    last_status_report: Optional[Any]
    incident_priority: IncidentPriorityRead
    incident_type: IncidentTypeRead
    # participants: Any # List[IndividualReadNested]
    storage: Optional[StorageRead] = None
    ticket: Optional[TicketRead] = None
    documents: Optional[List[DocumentRead]] = []
    conversation: Optional[ConversationRead] = None
    visibility: Visibility

    created_at: Optional[datetime] = None
    reported_at: Optional[datetime] = None
    stable_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None


class IncidentPagination(DispatchBase):
    total: int
    items: List[IncidentRead] = []
