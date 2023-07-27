from typing import List, Optional
from pydantic import Field

from sqlalchemy import Table, Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint

from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import PrimaryKey, DispatchBase, ProjectMixin, Pagination
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
    __table_args__ = (UniqueConstraint("text", "project_id"),)
    id = Column(Integer, primary_key=True)
    text = Column(String)
    source = Column(String, default="dispatch")
    terms = relationship("Term", secondary=definition_terms, backref="definitions")
    teams = relationship("TeamContact", secondary=definition_teams)
    search_vector = Column(
        TSVectorType(
            "text",
            regconfig="pg_catalog.simple",
        )
    )


class DefinitionTerm(DispatchBase):
    id: Optional[PrimaryKey]
    text: Optional[str]


# Pydantic models...
class DefinitionBase(DispatchBase):
    text: str
    source: Optional[str] = Field(None, nullable=True)


class DefinitionCreate(DefinitionBase):
    terms: Optional[List[DefinitionTerm]] = []
    project: ProjectRead


class DefinitionUpdate(DefinitionBase):
    terms: Optional[List[DefinitionTerm]] = []


class DefinitionRead(DefinitionBase):
    id: PrimaryKey
    terms: Optional[List[DefinitionTerm]]


class DefinitionPagination(Pagination):
    items: List[DefinitionRead] = []
