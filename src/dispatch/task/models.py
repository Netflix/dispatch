from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, event
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, ResourceMixin, TimeStampMixin


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


class Task(Base, ResourceMixin, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    resolved_at = Column(DateTime)
    resolve_by = Column(DateTime, default=default_resolution_time)
    last_reminder_at = Column(DateTime)
    creator = Column(String)  # Should this be of type Participant?
    assignees = Column(String)  # Should this be of type Participant?
    description = Column(String)
    source = Column(String, default=TaskSource.incident)
    priority = Column(String, default=TaskPriority.low)
    status = Column(String, default=TaskStatus.open)
    reminders = Column(Boolean, default=True)
    incident_id = Column(Integer, ForeignKey("incident.id"))
    search_vector = Column(TSVectorType("description"))

    @staticmethod
    def _resolved_at(mapper, connection, target):
        if target.status == TaskStatus.resolved:
            target.resolved_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._resolved_at)


# Pydantic models
class TaskBase(DispatchBase):
    creator: Optional[str]
    created_at: Optional[datetime]
    resolved_at: Optional[datetime]
    resolve_by: Optional[datetime]
    updated_at: Optional[datetime]
    assignees: Optional[str]
    source: Optional[str]
    status: Optional[str]
    priority: Optional[str]
    description: Optional[str]
    weblink: Optional[str]


class TaskCreate(TaskBase):
    status: TaskStatus = TaskStatus.open


class TaskUpdate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int


class TaskPagination(DispatchBase):
    total: int
    items: List[TaskRead] = []
