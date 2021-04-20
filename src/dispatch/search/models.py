from typing import List, Optional

from pydantic import Field
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.schema import UniqueConstraint

from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin

from dispatch.project.models import ProjectRead
from dispatch.incident.models import IncidentReadNested
from dispatch.tag.models import TagRead
from dispatch.term.models import TermRead
from dispatch.definition.models import DefinitionRead
from dispatch.individual.models import IndividualContactRead
from dispatch.team.models import TeamContactRead
from dispatch.service.models import ServiceRead
from dispatch.document.models import DocumentRead
from dispatch.task.models import TaskRead


class SearchFilter(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON)
    creator_id = Column(Integer, ForeignKey("dispatch_user.id"))
    creator = relationship("DispatchUser", backref="search_filters")
    type = Column(String)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic models...
class SearchFilterBase(DispatchBase):
    expression: List[dict]
    name: Optional[str]
    type: Optional[str]
    description: Optional[str]


class SearchFilterCreate(SearchFilterBase):
    project: ProjectRead


class SearchFilterUpdate(SearchFilterBase):
    id: int


class SearchFilterRead(SearchFilterBase):
    id: int


class SearchFilterPagination(DispatchBase):
    items: List[SearchFilterRead]
    total: int


# Pydantic models...
class SearchBase(DispatchBase):
    query: Optional[str]


class SearchRequest(SearchBase):
    pass


class ContentResponse(DispatchBase):
    documents: Optional[List[DocumentRead]] = Field([], alias="Document")
    incidents: Optional[List[IncidentReadNested]] = Field([], alias="Incident")
    tasks: Optional[List[TaskRead]] = Field([], alias="Task")
    tags: Optional[List[TagRead]] = Field([], alias="Tag")
    terms: Optional[List[TermRead]] = Field([], alias="Term")
    definitions: Optional[List[DefinitionRead]] = Field([], alias="Definition")
    teams: Optional[List[TeamContactRead]] = Field([], alias="TeamContact")
    individuals: Optional[List[IndividualContactRead]] = Field([], alias="IndividualContact")
    services: Optional[List[ServiceRead]] = Field([], alias="Service")

    class Config:
        allow_population_by_field_name = True


class SearchResponse(DispatchBase):
    query: Optional[str]
    results: ContentResponse
