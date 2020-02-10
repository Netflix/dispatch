"""
.. module: dispatch.plugins.bases.application
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.models import PluginOptionModel
from dispatch.plugins.base import Plugin


class ApplicationPlugin(Plugin):
    type = "application"
    _schema = PluginOptionModel

    def get(self, **kwargs):
        raise NotImplementedError
