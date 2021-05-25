import time
import logging
from tabulate import tabulate
from os import path

from fastapi import FastAPI
from sentry_asgi import SentryMiddleware
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import FileResponse, Response, StreamingResponse
from starlette.routing import compile_path
from starlette.staticfiles import StaticFiles
import httpx


from .api import api_router
from .common.utils.cli import install_plugins, install_plugin_events
from .config import STATIC_DIR
from .database.core import engine, sessionmaker
from .extensions import configure_extensions
from .logging import configure_logging
from .metrics import provider as metric_provider


log = logging.getLogger(__name__)

# we configure the logging level and format
configure_logging()

# we configure the extensions such as Sentry
configure_extensions()

# we create the ASGI for the app
app = Starlette()

# we create the ASGI for the frontend
frontend = Starlette()

# we create the Web API framework
api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


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
        # starlette does not fill in the the params object until after the request, we do it manually
        path_params = {}
        for r in api_router.routes:
            path_regex, path_format, param_converters = compile_path(r.path)
            # remove the /api/v1 for matching
            path = f"/{request['path'].strip('/api/v1')}"
            match = path_regex.match(path)
            if match:
                path_params = match.groupdict()

        # if this call is organization specific set the correct search path
        organization_name = path_params.get("organization")
        if organization_name:
            # add correct schema mapping depending on the request
            schema_engine = engine.execution_options(
                schema_translate_map={None: f"dispatch_organization_{organization_name}"}
            )
            session = sessionmaker(bind=schema_engine)
        else:
            session = sessionmaker(bind=engine)

        if not session:
            return response

        request.state.db = session()
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


# we add a middleware class for logging exceptions to Sentry
app.add_middleware(SentryMiddleware)

# we add a middleware class for capturing metrics using Dispatch's metrics provider
app.add_middleware(MetricsMiddleware)

# we install all the plugins
install_plugins()

# we add all the plugin event API routes to the API router
install_plugin_events(api_router)

# we add all API routes to the Web API framework
api.include_router(api_router, prefix="/v1")

# we mount the frontend and app
if STATIC_DIR:
    frontend.mount("/", StaticFiles(directory=STATIC_DIR), name="app")

app.mount("/api", app=api)
app.mount("/", app=frontend)

# we print all the registered API routes to the console
table = []
for r in api_router.routes:
    auth = any(
        d.dependency.__name__ == "get_current_user" for d in r.dependencies
    )  # TODO this is fragile
    table.append([r.path, auth, ",".join(r.methods)])

log.debug("Available Endpoints \n" + tabulate(table, headers=["Path", "Authenticated", "Methods"]))
