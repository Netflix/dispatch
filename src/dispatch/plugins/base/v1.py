"""
.. module: dispatch.plugins.base.v1
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""

import logging
from threading import local

from pydantic import BaseModel
from typing import Any

logger = logging.getLogger(__name__)


class PluginConfiguration(BaseModel):
    pass


class IPluginEvent:
    name: str | None = None
    description: str | None = None


# stolen from https://github.com/getsentry/sentry/
class PluginMount(type):
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        if IPlugin in bases:
            return new_cls
        if new_cls.title is None:
            new_cls.title = new_cls.__name__
        if not new_cls.slug:
            new_cls.slug = new_cls.title.replace(" ", "-").lower()

        return new_cls


class IPlugin(local):
    """
    Plugin interface. Should not be inherited from directly.
    A plugin should be treated as if it were a singleton. The owner does not
    control when or how the plugin gets instantiated, nor is it guaranteed that
    it will happen, or happen more than once.
    >>> from dispatch.plugins import Plugin
    >>>
    >>> class MyPlugin(Plugin):
    >>>     def get_title(self):
    >>>         return 'My Plugin'
    As a general rule all inherited methods should allow ``**kwargs`` to ensure
    ease of future compatibility.
    """

    # Generic plugin information
    title: str | None = None
    slug: str | None = None
    description: str | None = None
    version: str | None = None
    author: str | None = None
    author_url: str | None = None
    configuration: dict | None = None
    project_id: int | None = None
    resource_links = ()

    schema: PluginConfiguration
    commands: list[Any] = []

    events: Any = None
    plugin_events: list[IPluginEvent | None] = []

    # Global enabled state
    enabled: bool = False
    can_disable: bool = True
    multiple: bool = False

    def is_enabled(self) -> bool:
        """
        Returns a boolean representing if this plugin is enabled.
        >>> plugin.is_enabled()
        """
        if not self.enabled:
            return False
        if not self.can_disable:
            return True
        return True

    def get_title(self) -> str | None:
        """
        Returns the general title for this plugin.
        >>> plugin.get_title()
        """
        return self.title

    def get_description(self) -> str | None:
        """
        Returns the description for this plugin. This is shown on the plugin configuration
        page.
        >>> plugin.get_description()
        """
        return self.description

    def get_resource_links(self) -> list[Any]:
        """
        Returns a list of tuples pointing to various resources for this plugin.
        >>> def get_resource_links(self):
        >>>     return [
        >>>         ('Documentation', 'https://dispatch.readthedocs.io'),
        >>>         ('Bug Tracker', 'https://github.com/Netflix/dispatch/issues'),
        >>>         ('Source', 'https://github.com/Netflix/dispatch'),
        >>>     ]
        """
        return self.resource_links

    def get_event(self, event) -> IPluginEvent | None:
        for plugin_event in self.plugin_events:
            if plugin_event.slug == event.slug:
                return plugin_event

    def fetch_events(self, **kwargs):
        raise NotImplementedError


class Plugin(IPlugin):
    """
    A plugin should be treated as if it were a singleton. The owner does not
    control when or how the plugin gets instantiated, nor is it guaranteed that
    it will happen, or happen more than once.
    """

    __version__ = 1
    __metaclass__ = PluginMount
