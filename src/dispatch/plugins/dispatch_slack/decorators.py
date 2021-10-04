from functools import wraps
import inspect
import logging
import time
import uuid

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from pydantic import BaseModel

from dispatch.exceptions import NotFoundError
from dispatch.conversation import service as conversation_service
from dispatch.database.core import engine, sessionmaker, SessionLocal
from dispatch.metrics import provider as metrics_provider
from dispatch.organization import service as organization_service
from dispatch.plugin import service as plugin_service
from dispatch.plugins.base.v1 import Plugin
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service


log = logging.getLogger(__name__)


def get_plugin_configuration_from_channel_id(db_session: SessionLocal, channel_id: str) -> Plugin:
    """Fetches the currently slack plugin configuration for this incident channel."""
    conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
        db_session, channel_id
    )
    if conversation:
        plugin_instance = plugin_service.get_active_instance(
            db_session=db_session,
            plugin_type="conversation",
            project_id=conversation.incident.project.id,
        )
        return plugin_instance.configuration


# we need a way to determine which organization to use for a given
# event, we use the unique channel id to determine which organization the
# event belongs to.
def get_organization_scope_from_channel_id(channel_id: str) -> SessionLocal:
    """Iterate all organizations looking for a relevant channel_id."""
    db_session = SessionLocal()
    organization_slugs = [o.slug for o in organization_service.get_all(db_session=db_session)]
    db_session.close()

    for slug in organization_slugs:
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: f"dispatch_organization_{slug}",
            }
        )

        scoped_db_session = sessionmaker(bind=schema_engine)()
        conversation = conversation_service.get_by_channel_id_ignoring_channel_type(
            db_session=scoped_db_session, channel_id=channel_id
        )
        if conversation:
            return scoped_db_session

        scoped_db_session.close()


def get_organization_scope_from_slug(slug: str) -> SessionLocal:
    """Iterate all organizations looking for a relevant channel_id."""
    db_session = SessionLocal()
    organization = organization_service.get_by_slug(db_session=db_session, slug=slug)
    db_session.close()

    if organization:
        schema_engine = engine.execution_options(
            schema_translate_map={
                None: f"dispatch_organization_{slug}",
            }
        )

        return sessionmaker(bind=schema_engine)()

    raise ValidationError(
        [
            ErrorWrapper(
                NotFoundError(msg=f"Organization slug '{slug}' not found. Check your spelling."),
                loc="organization",
            )
        ],
        model=BaseModel,
    )


def get_default_organization_scope() -> str:
    """Iterate all organizations looking for matching organization."""
    db_session = SessionLocal()
    organization = organization_service.get_default(db_session=db_session)
    db_session.close()

    schema_engine = engine.execution_options(
        schema_translate_map={
            None: f"dispatch_organization_{organization.slug}",
        }
    )

    return sessionmaker(bind=schema_engine)()


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

        metrics_provider.counter(
            "function.call.counter", tags={"function": fullname(func), "slack": True}
        )

        channel_id = kwargs["channel_id"]
        user_id = kwargs["user_id"]
        if not kwargs.get("db_session"):

            # slug passed directly is prefered over just having a channel_id
            organization_slug = kwargs.pop("organization_slug", None)
            if not organization_slug:
                scoped_db_session = get_organization_scope_from_channel_id(channel_id=channel_id)
                if not scoped_db_session:
                    scoped_db_session = get_default_organization_scope()
            else:
                scoped_db_session = get_organization_scope_from_slug(organization_slug)

            background = True
            kwargs["db_session"] = scoped_db_session

        if not kwargs.get("slack_client"):
            slack_client = dispatch_slack_service.create_slack_client(config=kwargs["config"])
            kwargs["slack_client"] = slack_client

        try:
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start
            metrics_provider.timer(
                "function.elapsed.time",
                value=elapsed_time,
                tags={"function": fullname(func), "slack": True},
            )
            return result
        except ValidationError as e:
            log.exception(e)
            message = f"Command Error: {e.errors()[0]['msg']}"

            dispatch_slack_service.send_ephemeral_message(
                client=kwargs["slack_client"],
                conversation_id=channel_id,
                user_id=user_id,
                text=message,
            )

        except Exception as e:
            # we generate our own guid for now, maybe slack provides us something we can use?
            slack_interaction_guid = str(uuid.uuid4())
            log.exception(e, extra=dict(slack_interaction_guid=slack_interaction_guid))

            # we notify the user that the interaction failed
            message = f"""Sorry, we've run into an unexpected error. For help please reach out to your Dispatch admins \
and provide them with the following token: '{slack_interaction_guid}'."""

            dispatch_slack_service.send_ephemeral_message(
                client=kwargs["slack_client"],
                conversation_id=channel_id,
                user_id=user_id,
                text=message,
            )
        finally:
            if background:
                kwargs["db_session"].close()

    return wrapper
