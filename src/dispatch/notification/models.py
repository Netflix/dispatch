from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, ForeignKey, Table, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.incident_priority.models import (
    IncidentPriorityCreate,
    IncidentPriorityRead,
    IncidentPriorityUpdate,
)
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead, IncidentTypeUpdate

from dispatch.models import DispatchBase, TimeStampMixin


# Association tables for many to many relationships
assoc_notification_incident_types = Table(
    "notification_incident_type",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id", ondelete="CASCADE")),
    Column("notification_id", Integer, ForeignKey("notification.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("incident_type_id", "notification_id"),
)

assoc_notification_incident_priorities = Table(
    "notification_incident_priority",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id", ondelete="CASCADE")),
    Column("notification_id", Integer, ForeignKey("notification.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("incident_priority_id", "notification_id"),
)


class Notification(Base, TimeStampMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    conversation_name = Column(String)
    conversation_description = Column(String)

    # Relationships
    incident_types = relationship(
        "IncidentType", secondary=assoc_notification_incident_types, backref="notifications"
    )
    incident_priorities = relationship(
        "IncidentPriority",
        secondary=assoc_notification_incident_priorities,
        backref="notifications",
    )

    search_vector = Column(TSVectorType("conversation_name", "conversation_description"))


# Pydantic models
class NotificationBase(DispatchBase):
    conversation_name: str
    conversation_description: Optional[str] = None


class NotificationCreate(NotificationBase):
    incident_types: Optional[List[IncidentTypeCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []


class NotificationUpdate(NotificationBase):
    incident_types: Optional[List[IncidentTypeUpdate]] = []
    incident_priorities: Optional[List[IncidentPriorityUpdate]] = []


class NotificationRead(NotificationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    incident_types: Optional[List[IncidentTypeRead]] = []
    incident_priorities: Optional[List[IncidentPriorityRead]] = []


class NotificationPagination(DispatchBase):
    total: int
    items: List[NotificationRead] = []
