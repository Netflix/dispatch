"""
.. module: dispatch.plugins.bases.oncall
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin
from dispatch.models import PluginOptionModel


class OncallPlugin(Plugin):
    type = "oncall"
    _schema = PluginOptionModel

    def get(self, service_id: str, **kwargs):
        raise NotImplementedError

    def page(
        self,
        service_id: str,
        incident_name: str,
        incident_title: str,
        incident_description: str,
        **kwargs,
    ):
        raise NotImplementedError
