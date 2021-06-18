import inspect
import logging
import time
from functools import wraps
from typing import Any, List

from dispatch.metrics import provider as metrics_provider

from .database.core import SessionLocal, engine, sessionmaker

from dispatch.organization import service as organization_service
from dispatch.project import service as project_service

log = logging.getLogger(__name__)


def fullname(o):
    module = inspect.getmodule(o)
    return f"{module.__name__}.{o.__qualname__}"


def scheduled_project_task(func):
    """Decorator that sets up a background task function with
    a database session and exception tracking.

    Each task is executed in a specific project context.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        db_session = SessionLocal()
        metrics_provider.counter("function.call.counter", tags={"function": fullname(func)})
        start = time.perf_counter()

        # iterate for all schema
        for organization in organization_service.get_all(db_session=db_session):
            schema_engine = engine.execution_options(
                schema_translate_map={None: f"dispatch_organization_{organization.slug}"}
            )
            schema_session = sessionmaker(bind=schema_engine)()
            kwargs["db_session"] = schema_session
            for project in project_service.get_all(db_session=schema_session):
                kwargs["project"] = project
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    log.exception(e)
            schema_session.close()
        elapsed_time = time.perf_counter() - start
        metrics_provider.timer(
            "function.elapsed.time", value=elapsed_time, tags={"function": fullname(func)}
        )
        db_session.close()

    return wrapper


def background_task(func):
    """Decorator that sets up the a background task function
    with a database session and exception tracking.

    As background tasks run in their own threads, it does not attempt
    to propagate errors.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        background = False
        if not kwargs.get("db_session"):
            if not kwargs.get("organization_slug"):
                raise Exception("If not db_session is supplied organization slug must be provided.")

            schema_engine = engine.execution_options(
                schema_translate_map={
                    None: f"dispatch_organization_{kwargs['organization_slug']}",
                }
            )
            db_session = sessionmaker(bind=schema_engine)

            background = True
            kwargs["db_session"] = db_session()
        try:
            metrics_provider.counter("function.call.counter", tags={"function": fullname(func)})
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start
            metrics_provider.timer(
                "function.elapsed.time", value=elapsed_time, tags={"function": fullname(func)}
            )
            return result
        except Exception as e:
            log.exception(e)
        finally:
            if background:
                kwargs["db_session"].close()

    return wrapper


def timer(func: Any):
    """Timing decorator that sends a timing metric."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_time = time.perf_counter() - start
        metrics_provider.timer(
            "function.elapsed.time", value=elapsed_time, tags={"function": fullname(func)}
        )
        return result

    return wrapper


def counter(func: Any):
    """Counting decorator that sends a counting metric."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        metrics_provider.counter("function.call.counter", tags={"function": fullname(func)})
        return func(*args, **kwargs)

    return wrapper


def apply(decorator: Any, exclude: List[str] = None):
    """Class decorator that applies specified decorator to all class methods."""
    if not exclude:
        exclude = []

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and attr not in exclude:
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate
