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
from dispatch.plugin.models import PluginCreate, PluginRead, PluginUpdate
from dispatch.tag.models import TagCreate, TagRead, TagUpdate
from dispatch.term.models import TermCreate, TermRead, TermUpdate

from dispatch.models import DispatchBase, TimeStampMixin


# Association tables for many-to-many relationships
notification_incident_type_assoc_table = Table(
    "notification_incident_type",
    Base.metadata,
    Column("notification_id", Integer, ForeignKey("notification.id", ondelete="CASCADE")),
    Column("incident_type_id", Integer, ForeignKey("incident_type.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("notification_id", "incident_type_id"),
)

notification_incident_priority_assoc_table = Table(
    "notification_incident_priority",
    Base.metadata,
    Column("notification_id", Integer, ForeignKey("notification.id", ondelete="CASCADE")),
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("notification_id", "incident_priority_id"),
)

notification_plugin_assoc_table = Table(
    "notification_plugin",
    Base.metadata,
    Column("notification_id", Integer, ForeignKey("notification.id", ondelete="CASCADE")),
    Column("plugin_id", Integer, ForeignKey("plugin.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("notification_id", "plugin_id"),
)

notification_tag_assoc_table = Table(
    "notification_tag",
    Base.metadata,
    Column("notification_id", Integer, ForeignKey("notification.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("notification_id", "tag_id"),
)

notification_term_assoc_table = Table(
    "notification_term",
    Base.metadata,
    Column("notification_id", Integer, ForeignKey("notification.id", ondelete="CASCADE")),
    Column("term_id", Integer, ForeignKey("term.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("notification_id", "term_id"),
)


class Notification(Base, TimeStampMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    type = Column(String)

    # Relationships
    incident_types = relationship(
        "IncidentType", secondary=notification_incident_type_assoc_table, backref="notifications"
    )
    incident_priorities = relationship(
        "IncidentPriority",
        secondary=notification_incident_priority_assoc_table,
        backref="notifications",
    )
    plugins = relationship(
        "Plugin", secondary=notification_plugin_assoc_table, backref="notifications"
    )
    tags = relationship("Tag", secondary=notification_tag_assoc_table, backref="notifications")
    terms = relationship("Term", secondary=notification_term_assoc_table, backref="notifications")

    search_vector = Column(TSVectorType("conversation_name", "conversation_description"))


# Pydantic models
class NotificationBase(DispatchBase):
    name: str
    description: Optional[str] = None
    type: str


class NotificationCreate(NotificationBase):
    incident_types: Optional[List[IncidentTypeCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    plugins: Optional[List[PluginCreate]] = []
    tags: Optional[List[TagCreate]] = []
    terms: Optional[List[TermCreate]] = []


class NotificationUpdate(NotificationBase):
    incident_types: Optional[List[IncidentTypeUpdate]] = []
    incident_priorities: Optional[List[IncidentPriorityUpdate]] = []
    plugins: Optional[List[PluginUpdate]] = []
    tags: Optional[List[TagUpdate]] = []
    terms: Optional[List[TermUpdate]] = []


class NotificationRead(NotificationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    incident_types: Optional[List[IncidentTypeRead]] = []
    incident_priorities: Optional[List[IncidentPriorityRead]] = []
    plugins: Optional[List[PluginRead]] = []
    tags: Optional[List[TagRead]] = []
    terms: Optional[List[TermRead]] = []


class NotificationPagination(DispatchBase):
    total: int
    items: List[NotificationRead] = []
