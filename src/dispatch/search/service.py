from typing import List

from sqlalchemy_searchable import search as search_db

from dispatch.common.utils.composite_search import CompositeSearch
from dispatch.database import Base


def composite_search(*, db_session, query_str: str, models: List[Base]):
    """Perform a multi-table search based on the supplied query."""
    s = CompositeSearch(db_session, models)
    q = s.build_query(query_str, sort=True)
    return s.search(query=q)


def search(*, db_session, query_str: str, model: Base):
    """Perform a search based on the query."""
    q = db_session.query(model)
    return search_db(q, query_str, sort=True)
