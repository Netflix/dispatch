from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from dispatch.tag.views import router as tag_router
from dispatch.auth.service import get_current_user
from dispatch.definition.views import router as definition_router
from dispatch.incident.views import router as incident_router
from dispatch.incident_priority.views import router as incident_priority_router
from dispatch.incident_type.views import router as incident_type_router
from dispatch.individual.views import router as individual_contact_router

from dispatch.policy.views import router as policy_router
from dispatch.route.views import router as route_router
from dispatch.search.views import router as search_router
from dispatch.service.views import router as service_router
from dispatch.team.views import router as team_contact_router
from dispatch.term.views import router as team_router
from dispatch.document.views import router as document_router
from dispatch.task.views import router as task_router
from dispatch.plugin.views import router as plugin_router
from dispatch.auth.views import user_router, auth_router
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
authenticated_api_router.include_router(user_router, prefix="/user", tags=["users"])
authenticated_api_router.include_router(document_router, prefix="/documents", tags=["documents"])
authenticated_api_router.include_router(tag_router, prefix="/tags", tags=["tags"])
authenticated_api_router.include_router(service_router, prefix="/services", tags=["services"])
authenticated_api_router.include_router(team_contact_router, prefix="/teams", tags=["teams"])
authenticated_api_router.include_router(
    individual_contact_router, prefix="/individuals", tags=["individuals"]
)
# authenticated_api_router.include_router(route_router, prefix="/route", tags=["route"])
authenticated_api_router.include_router(policy_router, prefix="/policies", tags=["policies"])
authenticated_api_router.include_router(
    definition_router, prefix="/definitions", tags=["definitions"]
)
authenticated_api_router.include_router(team_router, prefix="/terms", tags=["terms"])
authenticated_api_router.include_router(task_router, prefix="/tasks", tags=["tasks"])
authenticated_api_router.include_router(search_router, prefix="/search", tags=["search"])
authenticated_api_router.include_router(incident_router, prefix="/incidents", tags=["incidents"])
authenticated_api_router.include_router(
    incident_type_router, prefix="/incident_types", tags=["incident_types"]
)
authenticated_api_router.include_router(
    incident_priority_router, prefix="/incident_priorities", tags=["incident_priorities"]
)
authenticated_api_router.include_router(workflow_router, prefix="/workflows", tags=["workflows"])
authenticated_api_router.include_router(plugin_router, prefix="/plugins", tags=["plugins"])

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
