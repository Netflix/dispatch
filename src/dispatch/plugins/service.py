from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from .models import Plugin, PluginCreate, PluginUpdate
from .base import plugins


def get(*, db_session, plugin_id: int) -> Optional[Plugin]:
    """Returns a plugin based on the given plugin id."""
    return db_session.query(Plugin).filter(Plugin.id == plugin_id).one_or_none()


def get_all(*, db_session) -> List[Optional[Plugin]]:
    """Returns all plugins."""
    return db_session.query(Plugin)


def get_by_slug(*, db_session, slug: str) -> Plugin:
    """Fetches a given plugin or creates a new one."""
    return db_session.query(Plugin).filter(Plugin.slug == slug).one_or_none()


def create(*, db_session, plugin_in: PluginCreate) -> Plugin:
    """Creates a new plugin."""
    plugin = Plugin(**plugin_in.dict())
    db_session.add(plugin)
    db_session.commit()
    return plugin


def update(*, db_session, plugin: Plugin, plugin_in: PluginUpdate) -> Plugin:
    """Updates a plugin."""
    plugin_data = jsonable_encoder(plugin)
    update_data = plugin_in.dict(skip_defaults=True)

    # modify our current enablement in memory
    plugin_instance = plugins.get(plugin_in.slug)
    plugin_instance.enabled = plugin_in.enabled

    for field in plugin_data:
        if field in update_data:
            setattr(plugin, field, update_data[field])

    db_session.add(plugin)
    db_session.commit()
    return plugin


def delete(*, db_session, plugin_id: int):
    """Deletes a plugin."""
    db_session.query(Plugin).filter(Plugin.id == plugin_id).delete()
    db_session.commit()
