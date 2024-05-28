"""
.. module: dispatch.plugins.bases.incident_management
    :platform: Unix
    :copyright: (c) 2024 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: David Whittaker <dwhittaker@netflix.com>
"""
from dispatch.plugins.base import Plugin


class IncidentManagementPlugin(Plugin):
    type = "incident-management"

    def get(self, incident_id, **kwargs):
        raise NotImplementedError
