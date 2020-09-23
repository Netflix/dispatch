import traceback
import logging
import pkg_resources
from sqlalchemy.exc import SQLAlchemyError

from dispatch.plugins.base import plugins, register


logger = logging.getLogger(__name__)


# Plugin endpoints should determine authentication # TODO allow them to specify (kglisson)
def install_plugin_events(api):
    """Adds plugin endpoints to the event router."""
    for plugin in plugins.all():
        if plugin.events:
            api.include_router(plugin.events, prefix="/events", tags=["events"])


def install_plugins():
    """
    Installs plugins associated with dispatch
    :return:
    """

    for ep in pkg_resources.iter_entry_points("dispatch.plugins"):
        logger.info(f"Attempting to load plugin: {ep.name}")
        try:
            plugin = ep.load()
            register(plugin)
            logger.info(f"Successfully loaded plugin: {ep.name}")
        except SQLAlchemyError:
            logger.error(
                "Something went wrong with creating plugin rows, is the database setup correctly?"
            )
        except Exception:
            logger.error(f"Failed to load plugin {ep.name}:{traceback.format_exc()}")
        else:
            if not plugin.enabled:
                continue


def get_plugin_properties(json_schema):
    for _, v in json_schema["definitions"].items():
        return v["properties"]
