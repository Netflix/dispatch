"""
.. module: dispatch.plugins.bases.term
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin


class TermPlugin(Plugin):
    type = "term"

    def get(self, **kwargs):
        raise NotImplementedError
