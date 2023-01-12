import logging
import inspect
from functools import wraps
from typing import Callable, TypeVar
from typing_extensions import ParamSpec

log = logging.getLogger(__file__)

T = TypeVar("T")
P = ParamSpec("P")


class MessageDispatcher:
    """Dispatches current message to any registered function: https://github.com/slackapi/bolt-python/issues/786"""

    registered_funcs = []

    def add(self, *args, **kwargs):
        """Adds a function to the dispatcher."""

        def decorator(func):
            if not kwargs.get("name"):
                name = func.__name__
            else:
                name = kwargs.pop("name")

            self.registered_funcs.append({"name": name, "func": func})

        return decorator

    async def dispatch(self, *args, **kwargs):
        """Runs all registered functions."""
        for f in self.registered_funcs:
            # only inject the args the function cares about
            func_args = inspect.getfullargspec(inspect.unwrap(f["func"])).args
            injected_args = (kwargs[a] for a in func_args)

            try:
                await f["func"](*injected_args)
            except Exception as e:
                log.exception(e)
                log.debug(f"Failed to run dispatched function ({e})")


message_dispatcher = MessageDispatcher()


def handle_lazy_error(func: Callable[P, T]):
    """Surfaces tracable exceptions within lazy listener functions: https://github.com/slackapi/bolt-python/issues/635"""

    @wraps(func)
    async def handle(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            await func(*args, **kwargs)
        except Exception as error:
            log.debug(f"Failed to run a lazy listener function {func.__name__}")
            log.exception(f"{func.__name__}: {error}")

            from .bolt import app_error_handler

            client, body, respond = [kwargs.get(key) for key in ("client", "body", "respond")]
            await app_error_handler(error, client, body, log, respond)

    return handle
