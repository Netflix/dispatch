import logging
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from dispatch.exceptions import InvalidConfiguration
from dispatch.plugins.bases import OncallPlugin
from dispatch.project import service as project_service
from dispatch.service import service as service_service

from .models import Plugin, PluginInstance, PluginInstanceCreate, PluginInstanceUpdate


log = logging.getLogger(__name__)


def get(*, db_session, plugin_id: int) -> Optional[Plugin]:
    """Returns a plugin based on the given plugin id."""
    return db_session.query(Plugin).filter(Plugin.id == plugin_id).one_or_none()


def get_by_slug(*, db_session, slug: str) -> Plugin:
    """Fetches a plugin by slug."""
    return db_session.query(Plugin).filter(Plugin.slug == slug).one_or_none()


def get_all(*, db_session) -> List[Optional[Plugin]]:
    """Returns all plugins."""
    return db_session.query(Plugin)


def get_by_type(*, db_session, plugin_type: str) -> List[Optional[Plugin]]:
    """Fetches all plugins for a given type."""
    return db_session.query(Plugin).filter(Plugin.type == plugin_type).all()


def get_instance(*, db_session, plugin_instance_id: int) -> Optional[PluginInstance]:
    """Returns a plugin instance based on the given instance id."""
    return (
        db_session.query(PluginInstance)
        .filter(PluginInstance.id == plugin_instance_id)
        .one_or_none()
    )


def get_active_instance(
    *, db_session, plugin_type: str, project_id=None
) -> Optional[PluginInstance]:
    """Fetches the current active plugin for the given type."""
    plugin = (
        db_session.query(PluginInstance)
        .join(Plugin)
        .filter(Plugin.type == plugin_type)
        .filter(PluginInstance.project_id == project_id)
        .filter(PluginInstance.enabled == True)  # noqa
        .one_or_none()
    )

    if not plugin:
        log.error(
            f"Attempted to fetch active plugin, but none were found. PluginType: {plugin_type} ProjectId: {project_id}"
        )

    return plugin


def get_active_instance_by_slug(
    *, db_session, slug: str, project_id=None
) -> Optional[PluginInstance]:
    """Fetches the current active plugin for the given type."""
    plugin = (
        db_session.query(PluginInstance)
        .join(Plugin)
        .filter(Plugin.slug == slug)
        .filter(PluginInstance.project_id == project_id)
        .filter(PluginInstance.enabled == True)  # noqa
        .one_or_none()
    )

    if not plugin:
        log.error(
            f"Attempted to fetch active plugin, but none were found. PluginSlug: {slug} ProjectId: {project_id}"
        )

    return plugin


def get_enabled_instances_by_type(
    *, db_session, plugin_type: str
) -> List[Optional[PluginInstance]]:
    """Fetches all enabled plugins for a given type."""
    return (
        db_session.query(PluginInstance)
        .join(Plugin)
        .filter(Plugin.type == plugin_type)
        .filter(PluginInstance.enabled == True)  # noqa
        .all()
    )


def create_instance(*, db_session, plugin_instance_in: PluginInstanceCreate) -> PluginInstance:
    """Creates a new plugin instance."""
    project = project_service.get_by_name(
        db_session=db_session, name=plugin_instance_in.project.name
    )
    plugin = get(db_session=db_session, plugin_id=plugin_instance_in.plugin.id)
    plugin_instance = PluginInstance(
        **plugin_instance_in.dict(exclude={"project", "plugin"}), project=project, plugin=plugin
    )
    db_session.add(plugin_instance)
    db_session.commit()
    return plugin_instance


def update_instance(
    *, db_session, plugin_instance: PluginInstance, plugin_instance_in: PluginInstanceUpdate
) -> Plugin:
    """Updates a plugin instance."""
    plugin_data = jsonable_encoder(plugin_instance)
    update_data = plugin_instance_in.dict(skip_defaults=True)

    if plugin_instance_in.enabled:  # user wants to enable the plugin
        if not plugin_instance.plugin.multiple:
            # we can't have multiple plugins of this type disable the currently enabled one
            enabled_plugin_instances = get_enabled_instances_by_type(
                db_session=db_session, plugin_type=plugin_instance.plugin.type
            )
            if enabled_plugin_instances:
                enabled_plugin_instances[0].enabled = False
                db_session.add(enabled_plugin_instances[0])

    if not plugin_instance_in.enabled:  # user wants to disable the plugin
        if plugin_instance.plugin.type == OncallPlugin.type:
            oncall_services = service_service.get_all_by_type_and_status(
                db_session=db_session, service_type=plugin_instance.plugin.slug, is_active=True
            )
            if oncall_services:
                raise InvalidConfiguration(
                    f"Cannot disable plugin instance: {plugin_instance.plugin.title}. One or more oncall services depend on it. "
                )

    for field in plugin_data:
        if field in update_data:
            setattr(plugin_instance, field, update_data[field])

    db_session.add(plugin_instance)
    db_session.commit()
    return plugin_instance


def delete_instance(*, db_session, plugin_instance_id: int):
    """Deletes a plugin instance."""
    db_session.query(PluginInstance).filter(PluginInstance.id == plugin_instance_id).delete()
    db_session.commit()
