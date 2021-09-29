"""
.. module: dispatch.plugins.bases.conference
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin


class ConferencePlugin(Plugin):
    type = "conference"

    def create(self, items, **kwargs):
        raise NotImplementedError
