from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, Integer, String

from dispatch.database import Base
from dispatch.models import DispatchBase


class IncidentPriorityType(str, Enum):
    # Note: The reporting form uses these types for the Priority drop-down list. Add them in the order you want
    # them to be displayed.

    high = "High"
    medium = "Medium"
    low = "Low"
    info = "Info"


class IncidentPriority(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, default=IncidentPriorityType.info, unique=True)
    description = Column(String)


# Pydantic models...
class IncidentPriorityBase(DispatchBase):
    name: str
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
