import logging
import time
from contextvars import ContextVar
from os import path
from typing import Final, Optional
from uuid import uuid1

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sentry_asgi import SentryMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import inspect
from sqlalchemy.orm import scoped_session, sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, Response, StreamingResponse
from starlette.routing import compile_path
from starlette.staticfiles import StaticFiles

from .api import api_router
from .common.utils.cli import install_plugin_events, install_plugins
from .config import (
    STATIC_DIR,
)
from .database.core import engine
from .database.logging import SessionTracker
from .extensions import configure_extensions
from .logging import configure_logging
from .metrics import provider as metric_provider
from .rate_limiter import limiter

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
app = FastAPI(exception_handlers=exception_handlers, openapi_url="")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# we create the ASGI for the frontend
frontend = FastAPI(openapi_url="")
frontend.add_middleware(GZipMiddleware, minimum_size=1000)


@frontend.middleware("http")
async def default_page(request, call_next):
    response = await call_next(request)
    if response.status_code == 404:
        if STATIC_DIR:
            return FileResponse(path.join(STATIC_DIR, "index.html"))
    return response


# we create the Web API framework
api = FastAPI(
    title="Dispatch",
    description="Welcome to Dispatch's API documentation! Here you will able to discover all of the ways you can interact with the Dispatch API.",
    root_path="/api/v1",
    docs_url=None,
    openapi_url="/docs/openapi.json",
    redoc_url="/docs",
)
api.add_middleware(GZipMiddleware, minimum_size=1000)


def get_path_params_from_request(request: Request) -> str:
    path_params = {}
    for r in api_router.routes:
        path_regex, path_format, param_converters = compile_path(r.path)
        path = request["path"].removeprefix("/api/v1")  # remove the /api/v1 for matching
        match = path_regex.match(path)
        if match:
            path_params = match.groupdict()
    return path_params


def get_path_template(request: Request) -> str:
    if hasattr(request, "path"):
        return ",".join(request.path.split("/")[1:])
    return ".".join(request.url.path.split("/")[1:])


REQUEST_ID_CTX_KEY: Final[str] = "request_id"
_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar(REQUEST_ID_CTX_KEY, default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx_var.get()


@api.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request_id = str(uuid1())

    # we create a per-request id such that we can ensure that our session is scoped for a particular request.
    # see: https://github.com/tiangolo/fastapi/issues/726
    ctx_token = _request_id_ctx_var.set(request_id)
    session = None

    try:
        path_params = get_path_params_from_request(request)

        # if this call is organization specific set the correct search path
        organization_slug = path_params.get("organization", "default")
        request.state.organization = organization_slug
        schema = f"dispatch_organization_{organization_slug}"

        # validate slug exists
        schema_names = inspect(engine).get_schema_names()
        if schema not in schema_names:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": [{"msg": f"Unknown database schema name: {schema}"}]},
            )

        # add correct schema mapping depending on the request
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: schema,
            }
        )

        session = scoped_session(sessionmaker(bind=schema_engine), scopefunc=get_request_id)
        request.state.db = session()

        # we track the session
        request.state.db._dispatch_session_id = SessionTracker.track_session(
            request.state.db, context=f"api_request_{organization_slug}"
        )

        response = await call_next(request)

        # If we got here without exceptions, commit any pending changes
        if hasattr(request.state, "db") and request.state.db.is_active:
            request.state.db.commit()

        return response

    except Exception as e:
        # Explicitly rollback on exceptions
        try:
            if hasattr(request.state, "db") and request.state.db.is_active:
                request.state.db.rollback()
        except Exception as rollback_error:
            logging.error(f"Error during rollback: {rollback_error}")

        # Re-raise the original exception
        raise e from None
    finally:
        # Always clean up resources
        if hasattr(request.state, "db"):
            # Untrack the session
            if hasattr(request.state.db, "_dispatch_session_id"):
                try:
                    SessionTracker.untrack_session(request.state.db._dispatch_session_id)
                except Exception as untrack_error:
                    logging.error(f"Failed to untrack session: {untrack_error}")

            # Close the session
            try:
                request.state.db.close()
                if session is not None:
                    session.remove()  # Remove the session from the registry
            except Exception as close_error:
                logging.error(f"Error closing database session: {close_error}")

        # Always reset the context variable
        _request_id_ctx_var.reset(ctx_token)


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

        try:
            start = time.perf_counter()
            response = await call_next(request)
            elapsed_time = time.perf_counter() - start
            tags.update({"status_code": response.status_code})
            metric_provider.counter("server.call.counter", tags=tags)
            metric_provider.timer("server.call.elapsed", value=elapsed_time, tags=tags)
            log.debug(f"server.call.elapsed.{path_template}: {elapsed_time}")
        except Exception as e:
            metric_provider.counter("server.call.exception.counter", tags=tags)
            raise e from None
        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> StreamingResponse:
        try:
            response = await call_next(request)
        except ValidationError as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": e.errors()}
            )
        except ValueError as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": [{"msg": "Unknown", "loc": ["Unknown"], "type": "Unknown"}]},
            )
        except Exception as e:
            log.exception(e)
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": [{"msg": "Unknown", "loc": ["Unknown"], "type": "Unknown"}]},
            )

        return response


# we add a middleware class for logging exceptions to Sentry
api.add_middleware(SentryMiddleware)

# we add a middleware class for capturing metrics using Dispatch's metrics provider
api.add_middleware(MetricsMiddleware)

api.add_middleware(ExceptionMiddleware)

# we install all the plugins
install_plugins()

# we add all the plugin event API routes to the API router
install_plugin_events(api_router)

# we add all API routes to the Web API framework
api.include_router(api_router)

# we mount the frontend and app
if STATIC_DIR and path.isdir(STATIC_DIR):
    frontend.mount("/", StaticFiles(directory=STATIC_DIR), name="app")

app.mount("/api/v1", app=api)
app.mount("/", app=frontend)
