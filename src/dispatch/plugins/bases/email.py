"""
.. module: dispatch.plugins.bases.email
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin


class EmailPlugin(Plugin):
    type = "email"

    def send(self, items, **kwargs):
        raise NotImplementedError
