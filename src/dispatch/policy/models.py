from typing import List, Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase


class Policy(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    expression = Column(String)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic models...
class PolicyBase(DispatchBase):
    expression: str
    name: Optional[str]
    description: Optional[str]


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(PolicyBase):
    id: int


class PolicyRead(PolicyBase):
    id: int


class PolicyPagination(DispatchBase):
    items: List[PolicyRead]
    total: int
