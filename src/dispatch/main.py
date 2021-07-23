import time
import logging
from os import path

from fastapi import FastAPI, HTTPException, status
from fastapi import exceptions
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from sentry_asgi import SentryMiddleware
from sqlalchemy import inspect
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.routing import compile_path

from sqlalchemy_filters.exceptions import BadFilterFormat, FieldNotFound

from starlette.responses import FileResponse, Response, StreamingResponse
from starlette.staticfiles import StaticFiles
import httpx
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from .api import api_router
from .common.utils.cli import install_plugins, install_plugin_events
from .config import (
    STATIC_DIR,
)
from .database.core import MissingTable, engine, sessionmaker
from .extensions import configure_extensions
from .logging import configure_logging
from .metrics import provider as metric_provider


log = logging.getLogger(__name__)

# we configure the logging level and format
configure_logging()

# we configure the extensions such as Sentry
configure_extensions()


async def not_found(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": [{"msg": "Not Found."}]}
    )


exception_handlers = {404: not_found}

# we create the ASGI for the app
app = FastAPI(exception_handlers=exception_handlers)

# we create the ASGI for the frontend
frontend = FastAPI()

# we create the Web API framework
api = FastAPI(
    title="Dispatch",
    description="Welcome to Dispatch's API documentation! Here you will able to discover all of the ways you can interact with the Dispatch API.",
    root_path="/api/v1",
    docs_url=None,
    openapi_url="/docs/openapi.json",
    redoc_url="/docs",
)


def get_path_params_from_request(request: Request) -> str:
    path_params = {}
    for r in api_router.routes:
        path_regex, path_format, param_converters = compile_path(r.path)
        # remove the /api/v1 for matching
        path = f"/{request['path'].strip('/api/v1')}"
        match = path_regex.match(path)
        if match:
            path_params = match.groupdict()
    return path_params


def get_path_template(request: Request) -> str:
    if hasattr(request, "path"):
        return ",".join(request.path.split("/")[1:4])
    return ".".join(request.url.path.split("/")[1:4])


@frontend.middleware("http")
async def default_page(request: Request, call_next):
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


@api.middleware("http")
async def db_session_middleware(request: Request, call_next):
    path_params = get_path_params_from_request(request)

    # if this call is organization specific set the correct search path
    organization_slug = path_params.get("organization")
    if organization_slug:
        schema = f"dispatch_organization_{organization_slug}"
        # validate slug exists
        schema_names = inspect(engine).get_schema_names()
        if schema in schema_names:
            # add correct schema mapping depending on the request
            schema_engine = engine.execution_options(
                schema_translate_map={
                    None: schema,
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": [{"msg": "Forbidden"}]},
            )
    else:
        # add correct schema mapping depending on the request
        # can we set some default here?
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: "dispatch_organization_default",
            }
        )
    try:
        session = sessionmaker(bind=schema_engine)

        request.state.db = session()
        request.state.organization = organization_slug
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

        method = request.method
        tags = {"method": method, "endpoint": path_template}

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_time = time.perf_counter() - start
        tags.update({"status_code": response.status_code})
        metric_provider.timer("server.call.elapsed", value=elapsed_time, tags=tags)
        metric_provider.counter("server.call.counter", tags=tags)

        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path_template = get_path_template(request)

        method = request.method
        tags = {"method": method, "endpoint": path_template}
        print(request.method)

        try:
            return await call_next(request)
        except BadFilterFormat as e:
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": [{"msg": str(e), "loc": ["filter"], "type": "BadFilterFormat"}]},
            )
        except FieldNotFound as e:
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": [{"msg": str(e), "loc": ["filter"], "type": "FieldNotFound"}]},
            )
        except RequestValidationError as e:
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({"detail": e.errors()}),
            )
        except MissingTable as e:
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder(
                    {"detail": [{"msg": str(e), "loc": ["filter"], "type": "BadModel"}]}
                ),
            )
        except HTTPException as e:
            response = JSONResponse(status_code=e.status_code, content=e.detail)
        except Exception as e:
            response = JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": [{"msg": str(e)}]}
            )

        metric_provider.counter("server.call.exception.counter", tags=tags)
        return response


# we add a middleware class for logging exceptions to Sentry
api.add_middleware(SentryMiddleware)

# we add a middleware class for capturing metrics using Dispatch's metrics provider
api.add_middleware(MetricsMiddleware)

# we add exception middleware class for handling exception responses
api.add_middleware(ExceptionMiddleware)

# we install all the plugins
install_plugins()

# we add all the plugin event API routes to the API router
install_plugin_events(api_router)

# we add all API routes to the Web API framework
api.include_router(api_router)

# we mount the frontend and app
if STATIC_DIR:
    frontend.mount("/", StaticFiles(directory=STATIC_DIR), name="app")

app.mount("/api/v1", app=api)
app.mount("/", app=frontend)
