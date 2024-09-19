"""
.. module: dispatch.plugins.bases.artificial_intelligence
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""

from dispatch.plugins.base import Plugin


class ArtificialIntelligencePlugin(Plugin):
    type = "artificial-intelligence"

    def chat_completion(self, items, **kwargs):
        raise NotImplementedError

    def list_models(self, items, **kwargs):
        raise NotImplementedError
