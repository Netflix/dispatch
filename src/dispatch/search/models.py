from typing import Union, List, Optional

from dispatch.models import DispatchBase

from dispatch.incident.models import IncidentReadNested
from dispatch.tag.models import TagRead
from dispatch.term.models import TermRead
from dispatch.definition.models import DefinitionRead
from dispatch.individual.models import IndividualContactRead
from dispatch.team.models import TeamContactRead
from dispatch.service.models import ServiceRead
from dispatch.document.models import DocumentRead


# Pydantic models...
class SearchBase(DispatchBase):
    query: Optional[str]


class SearchRequest(SearchBase):
    pass


class ContentBase(DispatchBase):
    type: str
    content: Union[
        IncidentReadNested,
        TagRead,
        TermRead,
        DefinitionRead,
        IndividualContactRead,
        TeamContactRead,
        ServiceRead,
        DocumentRead,
    ]


class SearchResponse(SearchBase):
    results: List[ContentBase]
