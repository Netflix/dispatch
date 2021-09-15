"""
.. module: dispatch.plugins.bases.tag
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin


class TagPlugin(Plugin):
    type = "tag"

    def get(self, **kwargs):
        raise NotImplementedError
