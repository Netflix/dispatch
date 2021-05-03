from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from dispatch.auth.service import get_current_user
from dispatch.auth.views import user_router, auth_router
from dispatch.organization.views import router as organization_router
from dispatch.project.views import router as project_router
from dispatch.definition.views import router as definition_router
from dispatch.document.views import router as document_router
from dispatch.feedback.views import router as feedback_router
from dispatch.incident.views import router as incident_router
from dispatch.incident_cost.views import router as incident_cost_router
from dispatch.incident_cost_type.views import router as incident_cost_type_router
from dispatch.incident_priority.views import router as incident_priority_router
from dispatch.incident_type.views import router as incident_type_router
from dispatch.individual.views import router as individual_contact_router
from dispatch.notification.views import router as notification_router
from dispatch.plugin.views import router as plugin_router

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

from .config import DISPATCH_AUTHENTICATION_PROVIDER_SLUG

api_router = APIRouter(
    default_response_class=JSONResponse
)  # WARNING: Don't use this unless you want unauthenticated routes
authenticated_api_router = APIRouter()

# NOTE we only advertise auth routes when basic auth is enabled
if DISPATCH_AUTHENTICATION_PROVIDER_SLUG == "dispatch-auth-provider-basic":
    api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# NOTE: All api routes should be authenticated by default
authenticated_api_router.include_router(
    organization_router, prefix="/organizations", tags=["organizations"]
)
authenticated_api_router.include_router(
    project_router, prefix="/{organization}/projects", tags=["projects"]
)
authenticated_api_router.include_router(user_router, prefix="/{organization}/users", tags=["users"])
authenticated_api_router.include_router(
    document_router, prefix="/{organization}/documents", tags=["documents"]
)
authenticated_api_router.include_router(tag_router, prefix="/{organization}/tags", tags=["tags"])
authenticated_api_router.include_router(
    tag_type_router, prefix="/{organization}/tag_types", tags=["tag_types"]
)
authenticated_api_router.include_router(
    service_router, prefix="/{organization}/services", tags=["services"]
)
authenticated_api_router.include_router(
    team_contact_router, prefix="/{organization}/teams", tags=["teams"]
)
authenticated_api_router.include_router(
    individual_contact_router, prefix="/{organization}/individuals", tags=["individuals"]
)
# authenticated_api_router.include_router(route_router, prefix="/route", tags=["route"])
authenticated_api_router.include_router(
    definition_router, prefix="/{organization}/definitions", tags=["definitions"]
)
authenticated_api_router.include_router(term_router, prefix="/{organization}/terms", tags=["terms"])
authenticated_api_router.include_router(task_router, prefix="/{organization}/tasks", tags=["tasks"])
authenticated_api_router.include_router(
    search_router, prefix="/{organization}/search", tags=["search"]
)
authenticated_api_router.include_router(
    search_filter_router, prefix="/{organization}/search/filters", tags=["search_filters"]
)
authenticated_api_router.include_router(
    incident_router, prefix="/{organization}/incidents", tags=["incidents"]
)
authenticated_api_router.include_router(
    incident_type_router, prefix="/{organization}/incident_types", tags=["incident_types"]
)
authenticated_api_router.include_router(
    incident_priority_router,
    prefix="/{organization}/incident_priorities",
    tags=["incident_priorities"],
)
authenticated_api_router.include_router(
    workflow_router, prefix="/{organization}/workflows", tags=["workflows"]
)
authenticated_api_router.include_router(
    plugin_router, prefix="/{organization}/plugins", tags=["plugins"]
)
authenticated_api_router.include_router(
    feedback_router, prefix="/{organization}/feedback", tags=["feedback"]
)
authenticated_api_router.include_router(
    notification_router, prefix="/{organization}/notifications", tags=["notifications"]
)
authenticated_api_router.include_router(
    incident_cost_router, prefix="/{organization}/incident_costs", tags=["incident_costs"]
)
authenticated_api_router.include_router(
    incident_cost_type_router,
    prefix="/{organization}/incident_cost_types",
    tags=["incident_cost_types"],
)

doc_router = APIRouter()


@doc_router.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return JSONResponse(get_openapi(title="Dispatch Docs", version=1, routes=api_router.routes))


@doc_router.get("/", include_in_schema=False)
async def get_documentation():
    return get_redoc_html(openapi_url="/api/v1/docs/openapi.json", title="Dispatch Docs")


api_router.include_router(doc_router, prefix="/docs")


@api_router.get("/healthcheck", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}


api_router.include_router(authenticated_api_router, dependencies=[Depends(get_current_user)])
