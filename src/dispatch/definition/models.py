from typing import List, Optional

from sqlalchemy import Table, Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import (
    DispatchBase,
    ProjectMixin,
    TermNested,
    TermReadNested,
)
from dispatch.project.models import ProjectRead

# Association tables
definition_teams = Table(
    "definition_teams",
    Base.metadata,
    Column("definition_id", Integer, ForeignKey("definition.id")),
    Column("team_contact_id", Integer, ForeignKey("team_contact.id")),
    PrimaryKeyConstraint("definition_id", "team_contact_id"),
)

definition_terms = Table(
    "definition_terms",
    Base.metadata,
    Column("definition_id", Integer, ForeignKey("definition.id")),
    Column("term_id", Integer, ForeignKey("term.id")),
    PrimaryKeyConstraint("definition_id", "term_id"),
)


class Definition(Base, ProjectMixin):
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
    project: ProjectRead


class DefinitionUpdate(DefinitionBase):
    terms: Optional[List[TermReadNested]] = []


class DefinitionRead(DefinitionBase):
    id: int
    terms: Optional[List[TermReadNested]]


class DefinitionPagination(DispatchBase):
    total: int
    items: List[DefinitionRead] = []
