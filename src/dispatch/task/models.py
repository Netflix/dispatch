from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import Field

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
from dispatch.incident.models import IncidentReadMinimal
from dispatch.models import ResourceBase, ResourceMixin, PrimaryKey, Pagination
from dispatch.participant.models import ParticipantRead, ParticipantUpdate
from dispatch.project.models import ProjectRead

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
    assignees: List[Optional[ParticipantRead]] = []
    created_at: Optional[datetime]
    creator: Optional[ParticipantRead]
    description: Optional[str] = Field(None, nullable=True)
    incident: IncidentReadMinimal
    owner: Optional[ParticipantRead]
    priority: Optional[str] = Field(None, nullable=True)
    resolve_by: Optional[datetime]
    resolved_at: Optional[datetime]
    resource_id: Optional[str] = Field(None, nullable=True)
    source: Optional[str] = Field(None, nullable=True)
    status: TaskStatus = TaskStatus.open
    updated_at: Optional[datetime]


class TaskCreate(TaskBase):
    assignees: List[Optional[ParticipantUpdate]] = []
    creator: Optional[ParticipantUpdate]
    owner: Optional[ParticipantUpdate]
    resource_type: Optional[str]
    status: TaskStatus = TaskStatus.open


class TaskUpdate(TaskBase):
    assignees: List[Optional[ParticipantUpdate]] = []
    owner: Optional[ParticipantUpdate]
    creator: Optional[ParticipantUpdate]


class TaskRead(TaskBase):
    id: PrimaryKey
    project: Optional[ProjectRead]


class TaskPagination(Pagination):
    items: List[TaskRead] = []
