"""
.. module: dispatch.plugins.dispatch_pagerduty.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_mock_oncall as mock_oncall_plugin
from dispatch.plugins.bases import OncallPlugin

log = logging.getLogger(__name__)


@apply(timer)
@apply(counter)
class MockOncallPlugin(OncallPlugin):
    title = "Mock - Oncall - disable oncall feature"
    slug = "mock-oncall"
    description = "returns dummy datas for oncall infos"
    version = mock_oncall_plugin.__version__

    def get(self, service_id: str = None, service_name: str = None):
        """Gets the oncall person."""
        return "nobody@nomail.test"

    def page(
        self, service_id: str, incident_name: str, incident_title: str, incident_description: str
    ):
        """Pages the oncall person."""
        return 0
