"""
.. module: dispatch.plugins.bases.task
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin
from dispatch.models import PluginOptionModel


class TaskPlugin(Plugin):
    type = "task"
    _schema = PluginOptionModel

    def get(self, **kwargs):
        raise NotImplementedError

    def create(self, **kwargs):
        raise NotImplementedError

    def delete(self, **kwargs):
        raise NotImplementedError

    def list(self, **kwargs):
        raise NotImplementedError

    def resolve(self, **kwargs):
        raise NotImplementedError
