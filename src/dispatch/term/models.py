from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DefinitionNested, DefinitionReadNested, DispatchBase


# SQLAlchemy models...
class Term(Base):
    id = Column(Integer, primary_key=True)
    text = Column(String, unique=True)
    discoverable = Column(Boolean, default=True)
    search_vector = Column(TSVectorType("text"))


# Pydantic models...
class TermBase(DispatchBase):
    id: Optional[int] = None
    text: Optional[str] = None
    discoverable: Optional[bool] = True


class TermCreate(TermBase):
    definitions: Optional[List[DefinitionNested]] = []


class TermUpdate(TermBase):
    definitions: Optional[List[DefinitionNested]] = []


class TermRead(TermBase):
    id: int
    definitions: Optional[List[DefinitionReadNested]] = []


class TermPagination(DispatchBase):
    total: int
    items: List[TermRead] = []
