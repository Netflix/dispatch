"""
.. module: dispatch.plugins.base.manager
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson (kglisson@netflix.com)
"""
import logging
from dispatch.common.managers import InstanceManager


logger = logging.getLogger(__name__)


# inspired by https://github.com/getsentry/sentry
class PluginManager(InstanceManager):
    def __iter__(self):
        return iter(self.all())

    def __len__(self):
        return sum(1 for i in self.all())

    def all(self, version=1, plugin_type=None):
        for plugin in sorted(super(PluginManager, self).all(), key=lambda x: x.get_title()):
            if not plugin.type == plugin_type and plugin_type:
                continue
            if version is not None and plugin.__version__ != version:
                continue
            yield plugin

    def get(self, slug):
        for plugin in self.all(version=1):
            if plugin.slug == slug:
                return plugin
        for plugin in self.all(version=2):
            if plugin.slug == slug:
                return plugin
        logger.error(
            f"Unable to find slug: {slug} in self.all version 1: {self.all(version=1)} or version 2: {self.all(version=2)}"
        )
        raise KeyError(slug)

    def first(self, func_name, *args, **kwargs):
        version = kwargs.pop("version", 1)
        for plugin in self.all(version=version):
            try:
                result = getattr(plugin, func_name)(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error processing {func_name}() on {plugin.__class__}: {e}",
                    extra={"func_arg": args, "func_kwargs": kwargs},
                    exc_info=True,
                )
                continue

            if result is not None:
                return result

    def register(self, cls):
        self.add(f"{cls.__module__}.{cls.__name__}")
        return cls

    def unregister(self, cls):
        self.remove(f"{cls.__module__}.{cls.__name__}")
        return cls
