"""
.. module: dispatch.plugins.bases.ticket
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin
from dispatch.models import PluginOptionModel


class TicketPlugin(Plugin):
    type = "ticket"
    _schema = PluginOptionModel

    def create(self, ticket_id, **kwargs):
        raise NotImplementedError

    def update(self, ticket_id, **kwargs):
        raise NotImplementedError
