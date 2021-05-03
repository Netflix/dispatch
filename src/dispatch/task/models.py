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
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.config import INCIDENT_RESOURCE_INCIDENT_TASK
from dispatch.models import DispatchBase, ResourceBase, ResourceMixin

from dispatch.project.models import ProjectRead
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
    Column("participant_id", Integer, ForeignKey("participant.id", ondelete="CASCADE")),
    Column("task_id", Integer, ForeignKey("task.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("participant_id", "task_id"),
)

assoc_task_tickets = Table(
    "task_tickets",
    Base.metadata,
    Column("ticket_id", Integer, ForeignKey("ticket.id", ondelete="CASCADE")),
    Column("task_id", Integer, ForeignKey("task.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("ticket_id", "task_id"),
)


class Task(Base, ResourceMixin):
    id = Column(Integer, primary_key=True)
    resolved_at = Column(DateTime)
    resolve_by = Column(DateTime, default=default_resolution_time)
    last_reminder_at = Column(DateTime)
    creator_id = Column(Integer, ForeignKey("participant.id", ondelete="CASCADE"))
    owner_id = Column(Integer, ForeignKey("participant.id", ondelete="CASCADE"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))

    assignees = relationship(
        "Participant", secondary=assoc_task_assignees, backref="assigned_tasks", lazy="subquery"
    )
    description = Column(String)
    source = Column(String, default=TaskSource.incident)
    priority = Column(String, default=TaskPriority.low)
    status = Column(String, default=TaskStatus.open)
    reminders = Column(Boolean, default=True)

    # relationships
    tickets = relationship("Ticket", secondary=assoc_task_tickets, backref="tasks")

    search_vector = Column(TSVectorType("description"))

    @hybrid_property
    def project(self):
        return self.incident.project

    @staticmethod
    def _resolved_at(mapper, connection, target):
        if target.status == TaskStatus.resolved:
            target.resolved_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._resolved_at)


# Pydantic models
class TaskBase(ResourceBase):
    assignees: List[Optional[ParticipantRead]] = []
    created_at: Optional[datetime]
    creator: Optional[ParticipantRead]
    description: Optional[str]
    incident: Optional[IncidentReadNested]
    owner: Optional[ParticipantRead]
    priority: Optional[str]
    resolve_by: Optional[datetime]
    resolved_at: Optional[datetime]
    resource_id: Optional[str]
    source: Optional[str]
    status: TaskStatus = TaskStatus.open
    tickets: Optional[List[TicketRead]] = []
    updated_at: Optional[datetime]


class TaskCreate(TaskBase):
    assignees: List[Optional[ParticipantUpdate]] = []
    creator: Optional[ParticipantUpdate]
    owner: Optional[ParticipantUpdate]
    resource_type: Optional[str] = INCIDENT_RESOURCE_INCIDENT_TASK
    status: TaskStatus = TaskStatus.open


class TaskUpdate(TaskBase):
    assignees: List[Optional[ParticipantUpdate]]
    owner: Optional[ParticipantUpdate]


class TaskRead(TaskBase):
    id: int
    project: Optional[ProjectRead]


class TaskPagination(DispatchBase):
    total: int
    items: List[TaskRead] = []
