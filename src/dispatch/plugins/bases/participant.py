"""
.. module: dispatch.plugins.bases.participant
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin


class ParticipantPlugin(Plugin):
    type = "participant"

    def get(self, items, **kwargs):
        raise NotImplementedError
