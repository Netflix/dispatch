from typing import List

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from dispatch.database.core import get_class_by_tablename
from dispatch.database.service import composite_search
from dispatch.database.service import common_parameters
from dispatch.enums import SearchTypes, UserRoles
from dispatch.enums import Visibility

from .models import (
    SearchResponse,
)

router = APIRouter()


@router.get("", response_class=JSONResponse)
def search(
    *,
    common: dict = Depends(common_parameters),
    type: List[str] = [
        v.value for v in SearchTypes
    ],  # hack for pydantic enum json generation see: https://github.com/samuelcolvin/pydantic/pull/1749
):
    """
    Perform a search.
    """
    if common["query_str"]:
        models = [get_class_by_tablename(t) for t in type]
        results = composite_search(
            db_session=common["db_session"],
            query_str=common["query_str"],
            models=models,
            current_user=common["current_user"],
        )
    else:
        results = []

    # add a filter for restricted incidents
    # TODO won't currently show incidents that you are a member
    admin_projects = []
    for p in common["current_user"].projects:
        if p.role == UserRoles.admin:
            admin_projects.append(p)

    filtered_incidents = []
    for incident in results["Incident"]:
        if incident.project in admin_projects or incident.visibility == Visibility.open.value:
            filtered_incidents.append(incident)

    results["Incident"] = filtered_incidents

    return SearchResponse(**{"query": common["query_str"], "results": results}).dict(by_alias=False)
