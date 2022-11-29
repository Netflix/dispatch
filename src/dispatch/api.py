from typing import List, Optional

from fastapi import APIRouter, Depends

from pydantic import BaseModel
from starlette.responses import JSONResponse

from dispatch.auth.service import get_current_user
from dispatch.auth.views import user_router, auth_router
from dispatch.case.priority.views import router as case_priority_router
from dispatch.case.severity.views import router as case_severity_router
from dispatch.case.type.views import router as case_type_router
from dispatch.case.views import router as case_router
from dispatch.data.alert.views import router as alert_router
from dispatch.data.query.views import router as query_router
from dispatch.data.source.data_format.views import router as source_data_format_router
from dispatch.data.source.environment.views import router as source_environment_router
from dispatch.data.source.status.views import router as source_status_router
from dispatch.data.source.transport.views import router as source_transport_router
from dispatch.data.source.type.views import router as source_type_router
from dispatch.data.source.views import router as source_router
from dispatch.definition.views import router as definition_router
from dispatch.document.views import router as document_router
from dispatch.feedback.views import router as feedback_router
from dispatch.incident.priority.views import router as incident_priority_router
from dispatch.incident.severity.views import router as incident_severity_router
from dispatch.incident.type.views import router as incident_type_router
from dispatch.incident.views import router as incident_router
from dispatch.incident_cost.views import router as incident_cost_router
from dispatch.incident_cost_type.views import router as incident_cost_type_router
from dispatch.incident_role.views import router as incident_role_router
from dispatch.individual.views import router as individual_contact_router
from dispatch.models import OrganizationSlug
from dispatch.notification.views import router as notification_router
from dispatch.organization.views import router as organization_router
from dispatch.plugin.views import router as plugin_router
from dispatch.project.views import router as project_router


from dispatch.signal.views import router as signal_router

# from dispatch.route.views import router as route_router
from dispatch.search.views import router as search_router
from dispatch.search_filter.views import router as search_filter_router
from dispatch.service.views import router as service_router
from dispatch.tag.views import router as tag_router
from dispatch.tag_type.views import router as tag_type_router
from dispatch.task.views import router as task_router
from dispatch.team.views import router as team_contact_router
from dispatch.term.views import router as term_router
from dispatch.workflow.views import router as workflow_router


class ErrorMessage(BaseModel):
    msg: str


class ErrorResponse(BaseModel):
    detail: Optional[List[ErrorMessage]]


api_router = APIRouter(
    default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

# WARNING: Don't use this unless you want unauthenticated routes
authenticated_api_router = APIRouter()


def get_organization_path(organization: OrganizationSlug):
    pass


api_router.include_router(auth_router, prefix="/{organization}/auth", tags=["auth"])

# NOTE: All api routes should be authenticated by default
authenticated_api_router.include_router(
    organization_router, prefix="/organizations", tags=["organizations"]
)

authenticated_organization_api_router = APIRouter(
    prefix="/{organization}", dependencies=[Depends(get_organization_path)]
)

authenticated_organization_api_router.include_router(
    project_router, prefix="/projects", tags=["projects"]
)

# Order matters for path eval
authenticated_organization_api_router.include_router(
    source_type_router, prefix="/data/sources/types", tags=["source_types"]
)
authenticated_organization_api_router.include_router(
    source_transport_router, prefix="/data/sources/transports", tags=["source_transports"]
)
authenticated_organization_api_router.include_router(
    source_status_router, prefix="/data/sources/statuses", tags=["source_statuses"]
)

authenticated_organization_api_router.include_router(
    source_data_format_router, prefix="/data/sources/dataFormats", tags=["source_data_formats"]
)

authenticated_organization_api_router.include_router(
    source_environment_router, prefix="/data/sources/environments", tags=["source_environments"]
)

authenticated_organization_api_router.include_router(
    source_router, prefix="/data/sources", tags=["sources"]
)

authenticated_organization_api_router.include_router(
    query_router, prefix="/data/queries", tags=["queries"]
)
authenticated_organization_api_router.include_router(
    alert_router, prefix="/data/alerts", tags=["alerts"]
)

authenticated_organization_api_router.include_router(
    signal_router, prefix="/signals", tags="signals"
)

authenticated_organization_api_router.include_router(user_router, prefix="/users", tags=["users"])
authenticated_organization_api_router.include_router(
    document_router, prefix="/documents", tags=["documents"]
)
authenticated_organization_api_router.include_router(tag_router, prefix="/tags", tags=["tags"])
authenticated_organization_api_router.include_router(
    tag_type_router, prefix="/tag_types", tags=["tag_types"]
)
authenticated_organization_api_router.include_router(
    service_router, prefix="/services", tags=["services"]
)
authenticated_organization_api_router.include_router(
    team_contact_router, prefix="/teams", tags=["teams"]
)
authenticated_organization_api_router.include_router(
    individual_contact_router, prefix="/individuals", tags=["individuals"]
)
# authenticated_api_router.include_router(route_router, prefix="/route", tags=["route"])
authenticated_organization_api_router.include_router(
    definition_router, prefix="/definitions", tags=["definitions"]
)
authenticated_organization_api_router.include_router(term_router, prefix="/terms", tags=["terms"])
authenticated_organization_api_router.include_router(task_router, prefix="/tasks", tags=["tasks"])
authenticated_organization_api_router.include_router(
    search_router, prefix="/search", tags=["search"]
)
authenticated_organization_api_router.include_router(
    search_filter_router, prefix="/search/filters", tags=["search_filters"]
)
authenticated_organization_api_router.include_router(
    incident_router, prefix="/incidents", tags=["incidents"]
)
authenticated_organization_api_router.include_router(
    incident_priority_router,
    prefix="/incident_priorities",
    tags=["incident_priorities"],
)
authenticated_organization_api_router.include_router(
    incident_severity_router,
    prefix="/incident_severities",
    tags=["incident_severities"],
)
authenticated_organization_api_router.include_router(
    incident_type_router, prefix="/incident_types", tags=["incident_types"]
)
authenticated_organization_api_router.include_router(case_router, prefix="/cases", tags=["cases"])
authenticated_organization_api_router.include_router(
    case_type_router, prefix="/case_types", tags=["case_types"]
)
authenticated_organization_api_router.include_router(
    case_priority_router,
    prefix="/case_priorities",
    tags=["case_priorities"],
)
authenticated_organization_api_router.include_router(
    case_severity_router,
    prefix="/case_severities",
    tags=["case_severities"],
)
authenticated_organization_api_router.include_router(
    workflow_router, prefix="/workflows", tags=["workflows"]
)
authenticated_organization_api_router.include_router(
    plugin_router, prefix="/plugins", tags=["plugins"]
)
authenticated_organization_api_router.include_router(
    feedback_router, prefix="/feedback", tags=["feedback"]
)
authenticated_organization_api_router.include_router(
    notification_router, prefix="/notifications", tags=["notifications"]
)
authenticated_organization_api_router.include_router(
    incident_cost_router, prefix="/incident_costs", tags=["incident_costs"]
)
authenticated_organization_api_router.include_router(
    incident_cost_type_router,
    prefix="/incident_cost_types",
    tags=["incident_cost_types"],
)
authenticated_organization_api_router.include_router(
    incident_role_router, prefix="/incident_roles", tags=["role"]
)


@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}


api_router.include_router(
    authenticated_organization_api_router, dependencies=[Depends(get_current_user)]
)

api_router.include_router(
    authenticated_api_router,
    dependencies=[Depends(get_current_user)],
)
