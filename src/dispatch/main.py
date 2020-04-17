import time
import logging
from tabulate import tabulate
from os import path

# from starlette.middleware.gzip import GZipMiddleware
from fastapi import FastAPI
from sentry_asgi import SentryMiddleware
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import FileResponse, Response, StreamingResponse
from starlette.staticfiles import StaticFiles
import httpx

from dispatch.conference.models import Conference  # noqa lgtm[py/unused-import]
from dispatch.team.models import TeamContact  # noqa lgtm[py/unused-import]
from dispatch.conversation.models import Conversation  # noqa lgtm[py/unused-import]
from dispatch.definition.models import Definition  # noqa lgtm[py/unused-import]
from dispatch.document.models import Document  # noqa lgtm[py/unused-import]
from dispatch.event.models import Event  # noqa lgtm[py/unused-import]
from dispatch.group.models import Group  # noqa lgtm[py/unused-import]
from dispatch.incident.models import Incident  # noqa lgtm[py/unused-import]
from dispatch.incident_priority.models import IncidentPriority  # noqa lgtm[py/unused-import]
from dispatch.incident_type.models import IncidentType  # noqa lgtm[py/unused-import]
from dispatch.individual.models import IndividualContact  # noqa lgtm[py/unused-import]
from dispatch.participant.models import Participant  # noqa lgtm[py/unused-import]
from dispatch.participant_role.models import ParticipantRole  # noqa lgtm[py/unused-import]
from dispatch.policy.models import Policy  # noqa lgtm[py/unused-import]
from dispatch.route.models import (
    Recommendation,
    RecommendationAccuracy,
)  # noqa lgtm[py/unused-import]
from dispatch.service.models import Service  # noqa lgtm[py/unused-import]
from dispatch.status_report.models import StatusReport  # noqa lgtm[py/unused-import]
from dispatch.storage.models import Storage  # noqa lgtm[py/unused-import]
from dispatch.tag.models import Tag  # noqa lgtm[py/unused-import]
from dispatch.task.models import Task  # noqa lgtm[py/unused-import]
from dispatch.term.models import Term  # noqa lgtm[py/unused-import]
from dispatch.ticket.models import Ticket  # noqa lgtm[py/unused-import]
from dispatch.plugin.models import Plugin  # noqa lgtm[py/unused-import]

from .api import api_router
from .config import STATIC_DIR
from .database import SessionLocal
from .metrics import provider as metric_provider
from .logging import configure_logging
from .extensions import configure_extensions
from .common.utils.cli import install_plugins, install_plugin_events

log = logging.getLogger(__name__)

app = Starlette()
frontend = Starlette()

api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

api.include_router(api_router, prefix="/v1")

if STATIC_DIR:
    frontend.mount("/", StaticFiles(directory=STATIC_DIR), name="app")

app.mount("/api", app=api)
app.mount("/", app=frontend)


def get_path_template(request: Request) -> str:
    if hasattr(request, "path"):
        return ",".join(request.path.split("/")[1:4])
    return ".".join(request.url.path.split("/")[1:4])


@frontend.middleware("http")
async def default_page(request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        if STATIC_DIR:
            return FileResponse(path.join(STATIC_DIR, "index.html"))
        else:
            async with httpx.AsyncClient() as client:
                remote_resp = await client.get(
                    str(request.url.replace(port=8080)), headers=dict(request.headers)
                )
                return StreamingResponse(
                    remote_resp.aiter_bytes(),
                    headers=remote_resp.headers,
                    status_code=remote_resp.status_code,
                    media_type=remote_resp.headers.get("content-type"),
                )
    return response


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal Server Error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000 ; includeSubDomains"
    return response


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path_template = get_path_template(request)

        # exclude non api requests e.g. static content
        if "api" not in path_template:
            return await call_next(request)

        method = request.method
        tags = {"method": method, "endpoint": path_template}

        try:
            start = time.perf_counter()
            response = await call_next(request)
            elapsed_time = time.perf_counter() - start
        except Exception as e:
            metric_provider.counter("server.call.exception.counter", tags=tags)
            raise e from None
        else:
            tags.update({"status_code": response.status_code})
            metric_provider.timer("server.call.elapsed", value=elapsed_time, tags=tags)
            metric_provider.counter("server.call.counter", tags=tags)

        return response


app.add_middleware(SentryMiddleware)
app.add_middleware(MetricsMiddleware)
# app.add_middleware(GZipMiddleware)

install_plugins()
install_plugin_events(api_router)

configure_logging()
configure_extensions()

table = []
for r in api_router.routes:
    auth = False
    for d in r.dependencies:
        if d.dependency.__name__ == "get_current_user":  # TODO this is fragile
            auth = True
    table.append([r.path, auth, ",".join(r.methods)])

log.debug("Available Endpoints \n" + tabulate(table, headers=["Path", "Authenticated", "Methods"]))
