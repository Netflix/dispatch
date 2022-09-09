"""
.. module: dispatch.plugins.dispatch_uptycs.plugin
    :platform: Unix
    :license: Apache, see LICENSE for more details.
"""
import json
import time
import logging
import datetime

from typing import List, Dict

import jwt
import requests

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_uptycs as uptycs_plugin
from dispatch.plugins.bases import SignalConsumerPlugin

from .config import UptycsConfiguration

log = logging.getLogger(__name__)


class UptycsAPI(object):
    def _uptycs_request(self, url: str, method: str = "GET", **kwargs):
        keys = json.loads(self.decrypted_key)
        inst_url = "ozark.uptycs.io"
        cust_id = keys["custid"]

        url = f"https://{inst_url}/public/api/customers/{cust_id}/{url}"

        ts = datetime.utcnow().timestamp()
        msg = {"iss": keys["apikey"], "iat": ts, "exp": ts + 60}
        auth = jwt.encode(msg, keys["apisecret"], algorithm="HS256")

        headers = {"Accept": "application/json", "Authorization": f"Bearer {auth}"}
        resp = requests.request(method, url, headers=headers, **kwargs)

        return resp.text if method == "DELETE" else resp.json()

    def _get_pageable_items(self, opage: str) -> List[Dict]:
        stime = time.time()
        page = opage
        ret = []
        while True:
            res = self._uptycs_request(page)
            ret.extend(res["items"])
            end = True
            for links in res["links"]:
                if links["rel"] == "next":
                    page = links["href"].split("/")[-1]
                    end = False
            if end:
                break
        log.debug(f"found {len(ret)} {opage} in {time.time()-stime}")
        return ret

    def get_alerts(self) -> List[Dict]:
        return self._get_pageable_items("alerts")


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class UptycsSignalConsumerPlugin(SignalConsumerPlugin):
    title = "Uptycs Plugin - Signal consumer"
    slug = "uptcs-signal-consumer"
    description = "Uses uptycs as a signal source."
    version = uptycs_plugin.__version__

    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = UptycsConfiguration

    def consume(self):
        """Enriches an event."""
        uapi = UptycsAPI()
        return uapi.get_alerts()
