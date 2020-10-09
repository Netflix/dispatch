"""
.. module: dispatch.plugins.dispatch_test.oncall
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from dispatch.plugins.bases import OncallPlugin


class TestOncallPlugin(OncallPlugin):
    title = "Dispatch Test Plugin - Oncall"
    slug = "test-oncall"
    description = "Oncall plugin for testing purposes"

    def get(self, service_id: str, **kwargs):
        return "johnsmith@example.com"

    def page(
        self,
        service_id: str,
        incident_name: str,
        incident_title: str,
        incident_description: str,
        **kwargs,
    ):
        return
