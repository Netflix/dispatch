"""
.. module: dispatch.plugins.bases.secondary_system
    :platform: Unix
    :copyright: (c) 2024 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: David Whittaker <dwhittaker@netflix.com>
"""
from dispatch.plugins.base import Plugin


class SecondarySystemPlugin(Plugin):
    type = "secondary-system"

    def chat(self, items, **kwargs):
        raise NotImplementedError

    def completion(self, items, **kwargs):
        raise NotImplementedError

    def summarization(self, items, **kwargs):
        raise NotImplementedError
