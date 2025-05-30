import traceback
import logging
from importlib.metadata import entry_points
from sqlalchemy.exc import SQLAlchemyError

from dispatch.plugins.base import plugins, register

logger = logging.getLogger(__name__)


# Plugin endpoints should determine authentication # TODO allow them to specify (kglisson)
def install_plugin_events(api):
    """Adds plugin endpoints to the event router."""
    for plugin in plugins.all():
        if plugin.events:
            api.include_router(plugin.events, prefix="/{organization}/events", tags=["events"])


def install_plugins():
    """Installs plugins associated with dispatch"""
    dispatch_plugins = entry_points().select(group="dispatch.plugins")

    for ep in dispatch_plugins:
        logger.info(f"Attempting to load plugin: {ep.name}")
        try:
            plugin = ep.load()
            register(plugin)
            logger.info(f"Successfully loaded plugin: {ep.name}")
        except SQLAlchemyError:
            logger.error(
                "Something went wrong with creating plugin rows, is the database setup correctly?"
            )
            logger.error(f"Failed to load plugin {ep.name}:{traceback.format_exc()}")
        except KeyError as e:
            logger.info(f"Failed to load plugin {ep.name} due to missing configuration items. {e}")
        except Exception:
            logger.error(f"Failed to load plugin {ep.name}:{traceback.format_exc()}")
