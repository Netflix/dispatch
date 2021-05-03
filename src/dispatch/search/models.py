from typing import List, Optional

from pydantic import Field

from dispatch.models import DispatchBase

from dispatch.incident.models import IncidentRead
from dispatch.tag.models import TagRead
from dispatch.term.models import TermRead
from dispatch.definition.models import DefinitionRead
from dispatch.individual.models import IndividualContactRead
from dispatch.team.models import TeamContactRead
from dispatch.service.models import ServiceRead
from dispatch.document.models import DocumentRead
from dispatch.task.models import TaskRead


# Pydantic models...
class SearchBase(DispatchBase):
    query: Optional[str]


class SearchRequest(SearchBase):
    pass


class ContentResponse(DispatchBase):
    documents: Optional[List[DocumentRead]] = Field([], alias="Document")
    incidents: Optional[List[IncidentRead]] = Field([], alias="Incident")
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
