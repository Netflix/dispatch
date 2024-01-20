import pytest


def test_get(session, plugin):
    from dispatch.plugin.service import get

    t_plugin = get(db_session=session, plugin_id=plugin.id)
    assert t_plugin.id == plugin.id


def test_get_instance(session, plugin_instance):
    from dispatch.plugin.service import get_instance

    t_plugin_instance = get_instance(db_session=session, plugin_instance_id=plugin_instance.id)
    assert t_plugin_instance.id == plugin_instance.id


@pytest.mark.skip
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


def test_get_plugin_event_by_id(*, session, plugin_event):
    """Returns a project based on the given project name."""
    from dispatch.plugin.service import get_plugin_event_by_id

    plugin_event_out = get_plugin_event_by_id(db_session=session, plugin_event_id=plugin_event.id)
    assert plugin_event_out
    assert plugin_event_out.id == plugin_event.id


def test_get_plugin_event_by_slug(*, session, plugin_event):
    """Returns a project based on the given project name."""
    from dispatch.plugin.service import get_plugin_event_by_slug

    plugin_event_out = get_plugin_event_by_slug(db_session=session, slug=plugin_event.slug)
    assert plugin_event_out
    assert plugin_event_out.id == plugin_event.id


def test_register_plugin_event(session, plugin):
    from dispatch.plugin.service import create_plugin_event, get_plugin_event_by_id
    from dispatch.plugin.models import PluginEventCreate

    plugin_event = create_plugin_event(
        db_session=session,
        plugin_event_in=PluginEventCreate(name="foo", slug="bar", plugin=plugin),
    )
    assert plugin_event

    plugin_event_out = get_plugin_event_by_id(db_session=session, plugin_event_id=plugin_event.id)
    assert plugin_event_out
    assert plugin_event_out.id == plugin_event.id


def test_get_all_events_for_plugin(*, session, plugin_event):
    from dispatch.plugin.service import get_all_events_for_plugin

    plugin_events_out = get_all_events_for_plugin(
        db_session=session, plugin_id=plugin_event.plugin.id
    )

    # Assert membership of plugin_event.
    is_member = False
    for plugin_event_out in plugin_events_out:
        if (
            plugin_event_out.id == plugin_event.id
            and plugin_event_out.name == plugin_event.name
            and plugin_event_out.plugin.id == plugin_event.plugin.id
            and plugin_event_out.description == plugin_event.description
            and plugin_event_out.slug == plugin_event.slug
        ):
            is_member = True
            break
    assert is_member
