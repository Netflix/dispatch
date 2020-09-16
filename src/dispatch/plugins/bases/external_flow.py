"""
.. module: dispatch.plugins.bases.external_flow
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin
from dispatch.models import PluginOptionModel


class ExternalFlowPlugin(Plugin):
    type = "external-flow"
    _schema = PluginOptionModel

    def list(self, **kwargs):
        raise NotImplementedError

    def run(self, **kwargs):
        raise NotImplementedError
