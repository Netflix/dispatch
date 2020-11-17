import inspect
import logging
import time
import uuid
from functools import wraps

from dispatch.metrics import provider as metrics_provider
from dispatch.database import SessionLocal
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service


log = logging.getLogger(__name__)


def fullname(o):
    module = inspect.getmodule(o)
    return f"{module.__name__}.{o.__qualname__}"


def slack_background_task(func):
    """Decorator that sets up the a slack background task function
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

        if not kwargs.get("slack_client"):
            slack_client = dispatch_slack_service.create_slack_client()
            kwargs["slack_client"] = slack_client

        try:
            metrics_provider.counter(
                "function.call.counter", tags={"function": fullname(func), "slack": True}
            )
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start
            metrics_provider.timer(
                "function.elapsed.time",
                value=elapsed_time,
                tags={"function": fullname(func), "slack": True},
            )
            return result
        except Exception as e:
            # we generate our own guid for now, maybe slack provides us something we can use?
            slack_interaction_guid = str(uuid.uuid4())
            log.exception(e, extra=dict(slack_interaction_guid=slack_interaction_guid))

            # notify the user the interaction failed
            message = f"Sorry, we've run into an unexpected error. For help, please reach out to the incident commander and provide them the following token: {slack_interaction_guid}"
            dispatch_slack_service.send_ephemeral_message(
                kwargs["slack_client"], kwargs["channel_id"], kwargs["user_id"], message
            )

        finally:
            if background:
                kwargs["db_session"].close()

    return wrapper
