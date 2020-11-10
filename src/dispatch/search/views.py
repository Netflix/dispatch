from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dispatch.auth.models import DispatchUser
from dispatch.auth.service import get_current_user

from dispatch.database import get_class_by_tablename, get_db
from dispatch.enums import SearchTypes, UserRoles

from dispatch.enums import Visibility

from .models import SearchResponse
from .service import composite_search

router = APIRouter()


@router.get("/", response_model=SearchResponse)
def search(
    *,
    db_session: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    q: str = None,
    type: List[str] = [
        v.value for v in SearchTypes
    ],  # hack for pydantic enum json generation see: https://github.com/samuelcolvin/pydantic/pull/1749
    current_user: DispatchUser = Depends(get_current_user),
):
    """
    Perform a search.
    """
    if q:
        models = [get_class_by_tablename(t) for t in type]
        results = composite_search(db_session=db_session, query_str=q, models=models)
    else:
        results = []

    # add a filter for restricted incidents
    if current_user.role != UserRoles.admin:
        filtered_results = []
        for r in results:
            if r["type"].lower() == "incident":
                if r["content"].visibility != Visibility.open:
                    continue
            filtered_results.append(r)
        results = filtered_results
    return {"query": q, "results": results}
