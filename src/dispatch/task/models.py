from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    event,
    Table,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.config import INCIDENT_RESOURCE_INCIDENT_TASK
from dispatch.models import DispatchBase, ResourceMixin, TimeStampMixin

from dispatch.incident.models import IncidentReadNested
from dispatch.ticket.models import TicketRead
from dispatch.participant.models import ParticipantRead, ParticipantUpdate


# SQLAlchemy models
class TaskStatus(str, Enum):
    open = "Open"
    resolved = "Resolved"


class TaskSource(str, Enum):
    incident = "Incident"
    post_incident_review = "Post Incident Review"


class TaskPriority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


def default_resolution_time(context):
    """Determines the default resolution time."""
    task_source = context.get_current_parameters()["source"]
    if task_source == TaskSource.incident:
        return datetime.utcnow() + timedelta(days=1)
    if task_source == TaskSource.post_incident_review:
        return datetime.utcnow() + timedelta(days=7)
    return datetime.utcnow() + timedelta(days=1)


assoc_task_assignees = Table(
    "task_assignees",
    Base.metadata,
    Column("participant_id", Integer, ForeignKey("participant.id")),
    Column("task_id", Integer, ForeignKey("task.id")),
    PrimaryKeyConstraint("participant_id", "task_id"),
)

assoc_task_tickets = Table(
    "task_tickets",
    Base.metadata,
    Column("ticket_id", Integer, ForeignKey("ticket.id")),
    Column("task_id", Integer, ForeignKey("task.id")),
    PrimaryKeyConstraint("ticket_id", "task_id"),
)


class Task(Base, ResourceMixin, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    resolved_at = Column(DateTime)
    resolve_by = Column(DateTime, default=default_resolution_time)
    last_reminder_at = Column(DateTime)
    creator_id = Column(Integer, ForeignKey("participant.id"))
    owner_id = Column(Integer, ForeignKey("participant.id"))
    assignees = relationship(
        "Participant", secondary=assoc_task_assignees, backref="assigned_tasks", lazy="subquery"
    )
    description = Column(String)
    source = Column(String, default=TaskSource.incident)
    priority = Column(String, default=TaskPriority.low)
    status = Column(String, default=TaskStatus.open)
    reminders = Column(Boolean, default=True)
    incident_id = Column(Integer, ForeignKey("incident.id"))
    search_vector = Column(TSVectorType("description"))
    tickets = relationship("Ticket", secondary=assoc_task_tickets, backref="tasks")

    @staticmethod
    def _resolved_at(mapper, connection, target):
        if target.status == TaskStatus.resolved:
            target.resolved_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._resolved_at)


# Pydantic models
class TaskBase(DispatchBase):
    creator: Optional[ParticipantRead]
    owner: Optional[ParticipantRead]
    created_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolve_by: Optional[datetime]
    updated_at: Optional[datetime]
    status: TaskStatus = TaskStatus.open
    assignees: List[Optional[ParticipantRead]] = []
    source: Optional[str]
    priority: Optional[str]
    description: Optional[str]
    tickets: Optional[List[TicketRead]] = []
    weblink: Optional[str]
    incident: Optional[IncidentReadNested]
    resource_id: Optional[str]


class TaskCreate(TaskBase):
    status: TaskStatus = TaskStatus.open
    assignees: List[Optional[ParticipantUpdate]] = []
    owner: Optional[ParticipantUpdate]
    creator: Optional[ParticipantUpdate]
    resource_type: Optional[str] = INCIDENT_RESOURCE_INCIDENT_TASK


class TaskUpdate(TaskBase):
    assignees: List[Optional[ParticipantUpdate]]
    owner: Optional[ParticipantUpdate]


class TaskRead(TaskBase):
    id: int


class TaskPagination(DispatchBase):
    total: int
    items: List[TaskRead] = []
