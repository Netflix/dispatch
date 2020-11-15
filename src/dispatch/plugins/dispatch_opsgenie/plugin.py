"""
.. module: dispatch.plugins.dispatch_opsgenie.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import OncallPlugin
from .service import get_oncall, page_oncall

__version__ = "0.1.0"
log = logging.getLogger(__name__)


@apply(timer)
@apply(counter)
class OpsGenieOncallPlugin(OncallPlugin):
    title = "OpsGenie Plugin - Oncall Management"
    slug = "opsgenie-oncall"
    author = "stefanm8"
    author_url = "https://github.com/Netflix/dispatch"
    description = "Uses Opsgenie to resolve and page oncall teams."
    version = __version__

    def get(self, service_id: str, **kwargs):
        return get_oncall()

    def page(
        self,
        service_id: str,
        incident_name: str,
        incident_title: str,
        incident_description: str,
        **kwargs,
    ):
        return page_oncall(incident_name, incident_title, incident_description)
