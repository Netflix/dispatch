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

    def get(self, incident_id, **kwargs):
        raise NotImplementedError
