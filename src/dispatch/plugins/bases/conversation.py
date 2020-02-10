"""
.. module: dispatch.plugins.bases.conversation
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin
from dispatch.models import PluginOptionModel


class ConversationPlugin(Plugin):
    type = "conversation"
    _schema = PluginOptionModel

    def create(self, items, **kwargs):
        raise NotImplementedError

    def add(self, items, **kwargs):
        raise NotImplementedError

    def send(self, items, **kwargs):
        raise NotImplementedError
