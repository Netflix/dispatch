"""
.. module: dispatch.plugins.bases.participant_group
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin
from dispatch.models import PluginOptionModel


class ParticipantGroupPlugin(Plugin):
    type = "participant-group"
    _schema = PluginOptionModel

    def create(self, participants, **kwargs):
        raise NotImplementedError

    def add(self, participant, **kwargs):
        raise NotImplementedError

    def remove(self, participant, **kwargs):
        raise NotImplementedError

    def delete(self, group, **kwargs):
        raise NotImplementedError

    def list(self, group, **kwargs):
        raise NotImplementedError
