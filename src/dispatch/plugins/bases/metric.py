"""
.. module: dispatch.plugins.bases.metric
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""

from dispatch.plugins.base import Plugin


class MetricPlugin(Plugin):
    type = "metric"

    def gauge(self, name, value, tags=None):
        raise NotImplementedError

    def counter(self, name, value=None, tags=None):
        raise NotImplementedError

    def timer(self, name, value, tags=None):
        raise NotImplementedError
