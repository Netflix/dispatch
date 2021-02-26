from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import TSVectorType, JSONType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin


# SQLAlchemy Model
class IncidentCostType(Base, TimeStampMixin):
    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=False)
    details = Column(JSONType, nullable=True)

    # full text search capabilities
    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic Models
class IncidentCostTypeBase(DispatchBase):
    name: str
    description: Optional[str]
    details: Optional[dict]


class IncidentCostTypeCreate(IncidentCostTypeBase):
    pass


class IncidentCostTypeUpdate(IncidentCostTypeBase):
    pass


class IncidentCostTypeRead(IncidentCostTypeBase):
    pass


class IncidentCostTypeNested(IncidentCostTypeBase):
    id: int
