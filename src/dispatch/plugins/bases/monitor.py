"""
.. module: dispatch.plugins.bases.monitor
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from dispatch.plugins.base import Plugin
from dispatch.models import PluginOptionModel


class MonitorPlugin(Plugin):
    type = "monitor"
    _schema = PluginOptionModel

    def get_status(self, **kwargs):
        raise NotImplementedError
