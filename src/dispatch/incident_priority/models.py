from typing import List, Optional
from pydantic import StrictBool

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase


class IncidentPriority(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    page_commander = Column(Boolean, default=False)

    # number of hours after which reports should be sent.
    tactical_report_reminder = Column(Integer, default=24, server_default="24")
    executive_report_reminder = Column(Integer, default=24, server_default="24")

    # This column is used to control how priorities should be displayed.
    # Lower orders will be shown first.
    view_order = Column(Integer, default=9999)

    search_vector = Column(TSVectorType("name", "description"))


# Pydantic models...
class IncidentPriorityBase(DispatchBase):
    name: str
    description: Optional[str]
    page_commander: Optional[StrictBool]
    tactical_report_reminder: Optional[int]
    executive_report_reminder: Optional[int]
    view_order: Optional[int]


class IncidentPriorityCreate(IncidentPriorityBase):
    pass


class IncidentPriorityUpdate(IncidentPriorityBase):
    pass


class IncidentPriorityRead(IncidentPriorityBase):
    id: int


class IncidentPriorityPagination(DispatchBase):
    total: int
    items: List[IncidentPriorityRead] = []
