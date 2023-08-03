from typing import List
from fastapi import APIRouter
from fastapi.params import Query
from starlette.responses import JSONResponse

from dispatch.database.core import get_class_by_tablename
from dispatch.database.service import composite_search
from dispatch.database.service import CommonParameters
from dispatch.enums import SearchTypes, UserRoles
from dispatch.enums import Visibility

from .models import (
    SearchResponse,
)

router = APIRouter()


@router.get("", response_class=JSONResponse)
def search(
    common: CommonParameters,
    type: List[SearchTypes] = Query(..., alias="type[]"),
):
    """Perform a search."""
    if common["query_str"]:
        models = [get_class_by_tablename(t) for t in type]
        results = composite_search(
            db_session=common["db_session"],
            query_str=common["query_str"],
            models=models,
            current_user=common["current_user"],
        )
        # add a filter for restricted incidents
        admin_projects = []
        for p in common["current_user"].projects:
            if p.role == UserRoles.admin:
                admin_projects.append(p)

        filtered_incidents = []
        current_user_email = common["current_user"].email
        for incident in results["Incident"]:
            participant_emails: list[str] = [
                participant.individual.email for participant in incident.participants
            ]
            if (
                incident.project in admin_projects
                or current_user_email in participant_emails
                or incident.visibility == Visibility.open
            ):
                filtered_incidents.append(incident)

        results["Incident"] = filtered_incidents

    else:
        results = []

    return SearchResponse(**{"query": common["query_str"], "results": results}).dict(by_alias=False)
