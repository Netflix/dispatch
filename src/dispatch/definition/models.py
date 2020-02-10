from typing import List, Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import (
    DispatchBase,
    TermNested,
    TermReadNested,
    definition_teams,
    definition_terms,
)


class Definition(Base):
    id = Column(Integer, primary_key=True)
    text = Column(String, unique=True)
    source = Column(String, default="dispatch")
    terms = relationship("Term", secondary=definition_terms, backref="definitions")
    teams = relationship("TeamContact", secondary=definition_teams)
    search_vector = Column(TSVectorType("text"))


# Pydantic models...
class DefinitionBase(DispatchBase):
    text: str
    source: Optional[str] = None


class DefinitionCreate(DefinitionBase):
    terms: Optional[List[TermNested]] = []


class DefinitionUpdate(DefinitionBase):
    terms: Optional[List[TermReadNested]] = []


class DefinitionRead(DefinitionBase):
    id: int
    terms: Optional[List[TermReadNested]]


class DefinitionPagination(DispatchBase):
    total: int
    items: List[DefinitionRead] = []
