from datetime import datetime, timedelta
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    event,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.incident.models import IncidentReadBasic
from dispatch.models import ResourceBase, ResourceMixin, PrimaryKey, Pagination
from dispatch.participant.models import ParticipantRead, ParticipantUpdate
from dispatch.project.models import ProjectRead
from dispatch.ticket.models import TicketRead

from .enums import TaskSource, TaskStatus, TaskPriority


def default_resolution_time(context):
    """Determines the default resolution time."""
    task_source = context.get_current_parameters()["source"]
    if task_source == TaskSource.incident:
        return datetime.utcnow() + timedelta(days=1)
    if task_source == TaskSource.post_incident_review:
        return datetime.utcnow() + timedelta(days=7)
    return datetime.utcnow() + timedelta(days=1)


# SQLAlchemy models
assoc_task_assignees = Table(
    "task_assignees",
    Base.metadata,
    Column("participant_id", Integer, ForeignKey("participant.id", ondelete="CASCADE")),
    Column("task_id", Integer, ForeignKey("task.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("participant_id", "task_id"),
)


class Task(Base, ResourceMixin):
    __table_args__ = (UniqueConstraint("resource_id", "incident_id"),)
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
    ticket = relationship("Ticket", uselist=False, backref="task", cascade="all, delete-orphan")

    search_vector = Column(
        TSVectorType(
            "description",
            regconfig="pg_catalog.simple",
        )
    )

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
    assignees: list[ParticipantRead | None] = []
    created_at: datetime | None
    creator: ParticipantRead | None
    description: str | None = None
    incident: IncidentReadBasic
    owner: ParticipantRead | None
    priority: str | None = None
    resolve_by: datetime | None
    resolved_at: datetime | None
    resource_id: str | None = None
    source: str | None = None
    status: TaskStatus = TaskStatus.open
    updated_at: datetime | None


class TaskCreate(TaskBase):
    assignees: list[ParticipantUpdate | None] = []
    creator: ParticipantUpdate | None
    owner: ParticipantUpdate | None
    resource_type: str | None
    status: TaskStatus = TaskStatus.open


class TaskUpdate(TaskBase):
    assignees: list[ParticipantUpdate | None] = []
    owner: ParticipantUpdate | None
    creator: ParticipantUpdate | None


class TaskRead(TaskBase):
    id: PrimaryKey
    project: ProjectRead | None
    ticket: TicketRead | None = None


class TaskPagination(Pagination):
    items: list[TaskRead] = []
