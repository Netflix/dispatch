from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import true
from sqlalchemy_utils import TSVectorType, JSONType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin


# SQLAlchemy Model
class IncidentCostType(Base, TimeStampMixin):
    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    details = Column(JSONType, nullable=True)
    default = Column(Boolean, default=False)
    editable = Column(Boolean, default=True)

    # full text search capabilities
    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic Models
class IncidentCostTypeBase(DispatchBase):
    name: str
    description: Optional[str]
    details: Optional[dict] = {}
    created_at: Optional[datetime]
    default: Optional[bool]
    editable: Optional[bool]


class IncidentCostTypeCreate(IncidentCostTypeBase):
    pass


class IncidentCostTypeUpdate(IncidentCostTypeBase):
    id: int


class IncidentCostTypeRead(IncidentCostTypeBase):
    id: int


class IncidentCostTypeNested(IncidentCostTypeBase):
    id: int


class IncidentCostTypePagination(DispatchBase):
    total: int
    items: List[IncidentCostTypeRead] = []
