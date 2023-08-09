from datetime import datetime
from typing import Optional, List
from pydantic import Field

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.enums import DispatchEnum
from dispatch.project.models import ProjectRead
from dispatch.search_filter.models import SearchFilterRead, SearchFilterUpdate

from dispatch.models import (
    EvergreenBase,
    EvergreenMixin,
    TimeStampMixin,
    ProjectMixin,
    NameStr,
    PrimaryKey,
    Pagination,
)


class NotificationTypeEnum(DispatchEnum):
    conversation = "conversation"
    email = "email"


assoc_notification_filters = Table(
    "assoc_notification_filters",
    Base.metadata,
    Column("notification_id", Integer, ForeignKey("notification.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("notification_id", "search_filter_id"),
)


class Notification(Base, TimeStampMixin, ProjectMixin, EvergreenMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    type = Column(String)
    target = Column(String)
    enabled = Column(Boolean, default=True)

    # Relationships
    filters = relationship(
        "SearchFilter", secondary=assoc_notification_filters, backref="notifications"
    )

    search_vector = Column(
        TSVectorType(
            "name",
            "description",
            regconfig="pg_catalog.simple",
        )
    )


# Pydantic models
class NotificationBase(EvergreenBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    type: NotificationTypeEnum
    target: str
    enabled: Optional[bool]


class NotificationCreate(NotificationBase):
    filters: Optional[List[SearchFilterRead]]
    project: ProjectRead


class NotificationUpdate(NotificationBase):
    filters: Optional[List[SearchFilterUpdate]]


class NotificationRead(NotificationBase):
    id: PrimaryKey
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    filters: Optional[List[SearchFilterRead]]


class NotificationPagination(Pagination):
    items: List[NotificationRead] = []
