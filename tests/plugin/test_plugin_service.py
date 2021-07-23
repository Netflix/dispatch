import pytest


def test_get(session, plugin):
    from dispatch.plugin.service import get

    t_plugin = get(db_session=session, plugin_id=plugin.id)
    assert t_plugin.id == plugin.id


def test_get_instance(session, plugin_instance):
    from dispatch.plugin.service import get_instance

    t_plugin_instance = get_instance(db_session=session, plugin_instance_id=plugin_instance.id)
    assert t_plugin_instance.id == plugin_instance.id


def test_get_all(session, plugins):
    from dispatch.plugin.service import get_all

    t_plugins = get_all(db_session=session).all()
    assert len(t_plugins) > 1


def test_create_instance(session, plugin, project):
    from dispatch.plugin.service import create_instance
    from dispatch.plugin.models import PluginInstanceCreate

    enabled = True
    configuration = {}

    plugin_instance_in = PluginInstanceCreate(
        enabled=enabled,
        configuration=configuration,
        plugin=plugin,
        project=project,
    )
    plugin_instance = create_instance(db_session=session, plugin_instance_in=plugin_instance_in)
    assert plugin_instance


@pytest.mark.skip
def test_update_instance(session, plugin_instance):
    from dispatch.plugin.service import update_instance
    from dispatch.plugin.models import PluginInstanceUpdate

    enabled = False

    plugin_instance_in = PluginInstanceUpdate(
        enabled=enabled,
    )
    plugin_instance = update_instance(
        db_session=session,
        plugin_instance=plugin_instance,
        plugin_instance_in=plugin_instance_in,
    )
    assert plugin_instance.enabled == enabled


def test_delete_instance(session, plugin_instance):
    from dispatch.plugin.service import delete_instance, get_instance

    delete_instance(db_session=session, plugin_instance_id=plugin_instance.id)
    assert not get_instance(db_session=session, plugin_instance_id=plugin_instance.id)
