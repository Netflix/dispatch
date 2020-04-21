import logging
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from .models import Plugin, PluginCreate, PluginUpdate


log = logging.getLogger(__name__)


def get(*, db_session, plugin_id: int) -> Optional[Plugin]:
    """Returns a plugin based on the given plugin id."""
    return db_session.query(Plugin).filter(Plugin.id == plugin_id).one_or_none()


def get_active(*, db_session, plugin_type: str) -> Optional[Plugin]:
    """Fetches the current active plugin for the given type."""
    return (
        db_session.query(Plugin)
        .filter(Plugin.type == plugin_type)
        .filter(Plugin.enabled == True)  # noqa
        .one_or_none()
    )


def get_by_type(*, db_session, plugin_type: str) -> List[Optional[Plugin]]:
    """Fetches all plugins for a given type."""
    return db_session.query(Plugin).filter(Plugin.type == plugin_type).all()


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

    # TODO can this be moved to a table trigger?
    # ensure that only one plugin is enabled per plugin type
    plugins_t = get_by_type(db_session=db_session, plugin_type=plugin.type)

    for p in plugins_t:
        if p.enabled:
            log.debug(f"Disabling existing plugin: {p.slug}")
            p.enabled = False
            db_session.add(p)

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
