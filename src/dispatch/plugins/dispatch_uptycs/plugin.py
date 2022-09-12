"""
.. module: dispatch.plugins.dispatch_uptycs.plugin
    :platform: Unix
    :license: Apache, see LICENSE for more details.
"""
import time
import logging

import jwt
import requests

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_uptycs as uptycs_plugin
from dispatch.plugins.bases import SignalConsumerPlugin

from .config import UptycsConfiguration

log = logging.getLogger(__name__)


def make_request(
    hostname: str,
    endpoint: str,
    customer_id: str,
    api_key: str,
    api_secret: str,
    method: str = "GET",
    **kwargs,
):
    url = f"https://{hostname}/api/customers/{customer_id}/{endpoint}"

    msg = {"iss": api_key.get_secret_value(), "exp": time.time() + 60 * 60 * 24 * 30}
    auth = jwt.encode(msg, api_secret.get_secret_value(), algorithm="HS256")

    headers = {"Accept": "application/json", "Authorization": f"Bearer {auth}"}
    resp = requests.request(method, url, headers=headers, **kwargs)

    return resp.text if method == "DELETE" else resp.json()


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class UptycsSignalConsumerPlugin(SignalConsumerPlugin):
    title = "Uptycs Plugin - Signal consumer"
    slug = "uptycs-signal-consumer"
    description = "Uses uptycs as a signal source."
    version = uptycs_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = UptycsConfiguration

    def consume(self):
        """Enriches an event."""
        data = make_request(
            hostname=self.configuration.hostname,
            endpoint="detections",
            customer_id=self.configuration.customer_id,
            api_key=self.configuration.api_key,
            api_secret=self.configuration.api_secret,
        )
        print(data)
        log.debug(f"Found {len(data['items'])} alerts.")
        return data
