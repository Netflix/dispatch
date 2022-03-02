"""
.. module: dispatch.plugins.bases.source
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin


class SourcePlugin(Plugin):
    type = "source"

    def get(self, **kwargs):
        raise NotImplementedError
