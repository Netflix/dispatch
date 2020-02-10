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
from starlette.responses import FileResponse, Response
from starlette.staticfiles import StaticFiles

from .api import api_router
from .config import STATIC_DIR
from .database import SessionLocal
from .metrics import provider as metric_provider
from .logging import configure_logging
from .extensions import configure_extensions

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
        return FileResponse(path.join(STATIC_DIR, "index.html"))
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
