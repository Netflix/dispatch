"""
.. module: dispatch.plugins.dispatch_pagerduty.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_pagerduty as pagerduty_oncall_plugin
from dispatch.plugins.bases import OncallPlugin

from .service import get_oncall, page_oncall


log = logging.getLogger(__name__)


@apply(timer)
@apply(counter)
class PagerDutyOncallPlugin(OncallPlugin):
    title = "PagerDuty Plugin - Oncall Management"
    slug = "pagerduty-oncall"
    description = "Uses PagerDuty to resolve and page oncall teams."
    version = pagerduty_oncall_plugin.__version__

    def get(self, service_id: str = None, service_name: str = None):
        """Gets the oncall person."""
        return get_oncall(service_id=service_id, service_name=service_name)

    def page(
        self, service_id: str, incident_name: str, incident_title: str, incident_description: str
    ):
        """Pages the oncall person."""
        return page_oncall(service_id, incident_name, incident_title, incident_description)
