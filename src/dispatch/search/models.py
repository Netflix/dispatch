from pydantic import Field

from dispatch.models import DispatchBase

from dispatch.definition.models import DefinitionRead
from dispatch.document.models import DocumentRead
from dispatch.incident.models import IncidentRead
from dispatch.case.models import CaseRead
from dispatch.individual.models import IndividualContactRead
from dispatch.service.models import ServiceRead
from dispatch.tag.models import TagRead
from dispatch.task.models import TaskRead
from dispatch.team.models import TeamContactRead
from dispatch.term.models import TermRead
from dispatch.data.source.models import SourceRead
from dispatch.data.query.models import QueryRead


# Pydantic models...
class SearchBase(DispatchBase):
    query: str | None = Field(None, nullable=True)


class SearchRequest(SearchBase):
    pass


class ContentResponse(DispatchBase):
    documents: list[DocumentRead] = Field([], alias="Document")
    incidents: list[IncidentRead] = Field([], alias="Incident")
    tasks: list[TaskRead] = Field([], alias="Task")
    tags: list[TagRead] = Field([], alias="Tag")
    terms: list[TermRead] = Field([], alias="Term")
    definitions: list[DefinitionRead] = Field([], alias="Definition")
    sources: list[SourceRead] = Field([], alias="Source")
    queries: list[QueryRead] = Field([], alias="Query")
    teams: list[TeamContactRead] = Field([], alias="TeamContact")
    individuals: list[IndividualContactRead] = Field([], alias="IndividualContact")
    services: list[ServiceRead] = Field([], alias="Service")
    cases: list[CaseRead] = Field([], alias="Case")

    class Config:
        allow_population_by_field_name = True


class SearchResponse(DispatchBase):
    query: str | None = Field(None, nullable=True)
    results: ContentResponse
