import inspect
import logging
import time
from functools import wraps
from typing import Any, List

from dispatch.metrics import provider as metrics_provider
from .database import SessionLocal


log = logging.getLogger(__name__)


def fullname(o):
    module = inspect.getmodule(o)
    return f"{module.__name__}.{o.__qualname__}"


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
            db_session = SessionLocal()
            background = True
            kwargs["db_session"] = db_session
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
