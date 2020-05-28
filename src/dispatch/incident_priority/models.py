from typing import List, Optional
from pydantic import StrictBool

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase


class IncidentPriority(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    page_commander = Column(Boolean, default=False)

    # This column is used to control how priorities should be displayed.
    # Lower orders will be shown first.
    view_order = Column(Integer, default=9999)

    # number of hours after which a tactical report should be sent.
    status_reminder = Column(Integer, default=24)
    description = Column(String)

    search_vector = Column(TSVectorType("name", "description"))


# Pydantic models...
class IncidentPriorityBase(DispatchBase):
    name: str
    page_commander: Optional[StrictBool]
    view_order: Optional[int]
    status_reminder: Optional[int]
    description: Optional[str]


class IncidentPriorityCreate(IncidentPriorityBase):
    pass


class IncidentPriorityUpdate(IncidentPriorityBase):
    pass


class IncidentPriorityRead(IncidentPriorityBase):
    id: int


class IncidentPriorityPagination(DispatchBase):
    total: int
    items: List[IncidentPriorityRead] = []
