"""Models for search functionality in the Dispatch application."""

from pydantic import ConfigDict, Field
from typing import ClassVar
from dispatch.case.models import CaseRead
from dispatch.data.query.models import QueryRead
from dispatch.data.source.models import SourceRead
from dispatch.definition.models import DefinitionRead
from dispatch.document.models import DocumentRead
from dispatch.incident.models import IncidentRead
from dispatch.individual.models import IndividualContactRead
from dispatch.models import DispatchBase
from dispatch.service.models import ServiceRead
from dispatch.tag.models import TagRead
from dispatch.task.models import TaskRead
from dispatch.team.models import TeamContactRead
from dispatch.term.models import TermRead


# Pydantic models...
class SearchBase(DispatchBase):
    """Base model for search queries."""

    query: str | None = None


class SearchRequest(SearchBase):
    """Model for a search request."""


class ContentResponse(DispatchBase):
    """Model for search content response."""

    documents: list[DocumentRead] | None = Field(default_factory=list, alias="Document")
    incidents: list[IncidentRead] | None = Field(default_factory=list, alias="Incident")
    tasks: list[TaskRead] | None = Field(default_factory=list, alias="Task")
    tags: list[TagRead] | None = Field(default_factory=list, alias="Tag")
    terms: list[TermRead] | None = Field(default_factory=list, alias="Term")
    definitions: list[DefinitionRead] | None = Field(default_factory=list, alias="Definition")
    sources: list[SourceRead] | None = Field(default_factory=list, alias="Source")
    queries: list[QueryRead] | None = Field(default_factory=list, alias="Query")
    teams: list[TeamContactRead] | None = Field(default_factory=list, alias="TeamContact")
    individuals: list[IndividualContactRead] | None = Field(
        default_factory=list, alias="IndividualContact"
    )
    services: list[ServiceRead] | None = Field(default_factory=list, alias="Service")
    cases: list[CaseRead] | None = Field(default_factory=list, alias="Case")
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)


class SearchResponse(DispatchBase):
    """Model for a search response."""

    query: str | None = None
    results: ContentResponse
