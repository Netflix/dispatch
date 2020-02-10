from typing import Any, List, Optional

from dispatch.models import DispatchBase


# Pydantic models...
class SearchBase(DispatchBase):
    query: Optional[str]


class SearchRequest(SearchBase):
    pass


class ContentBase(DispatchBase):
    type: str
    content: Any  # Union[TermRead, DefinitionRead, IndividualContactRead, TeamContactRead]


class SearchResponse(SearchBase):
    results: List[ContentBase]
