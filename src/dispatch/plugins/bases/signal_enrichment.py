"""
.. module: dispatch.plugins.bases.signal_enrichment
    :platform: Unix
    :copyright: (c) 2022 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin


class SignalEnrichmentPlugin(Plugin):
    type = "signal-enrichment"

    def enrich(self, **kwargs):
        raise NotImplementedError
