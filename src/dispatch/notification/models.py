from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.search.models import SearchFilterCreate, SearchFilterRead, SearchFilterUpdate

from dispatch.models import DispatchBase, TimeStampMixin


class Notification(Base, TimeStampMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    type = Column(String)
    target = Column(String)
    enabled = Column(Boolean, default=True)

    # Relationships
    search_filter_id = Column(Integer, ForeignKey("search_filter.id"))
    search_filter = relationship("SearchFilter", backref="notifications")

    search_vector = Column(TSVectorType("name", "description"))


# Pydantic models
class NotificationBase(DispatchBase):
    name: str
    description: Optional[str] = None
    type: str
    target: str
    enabled: Optional[bool]


class NotificationCreate(NotificationBase):
    search_filter: SearchFilterCreate


class NotificationUpdate(NotificationBase):
    search_filter: Optional[SearchFilterUpdate]


class NotificationRead(NotificationBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    search_filter: Optional[SearchFilterRead]


class NotificationPagination(DispatchBase):
    total: int
    items: List[NotificationRead] = []
