"""
.. module: dispatch.plugins.bases.monitor
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from dispatch.plugins.base import Plugin


class MonitorPlugin(Plugin):
    type = "monitor"

    def get_status(self, **kwargs):
        raise NotImplementedError
