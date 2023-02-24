"""
.. module: dispatch.plugins.dispatch_duo.plugin
    :platform: Unix
    :copyright: (c) 2023 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Will Sheldon <wshel@netflix.com>
"""
import logging
from typing import Optional

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_duo as duo_plugin
from dispatch.plugins.bases import MultiFactorAuthenticationPlugin
from dispatch.plugins.dispatch_duo import service as duo_service
from dispatch.plugins.dispatch_duo.config import DuoConfiguration

log = logging.getLogger(__name__)


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class DuoMfaPlugin(MultiFactorAuthenticationPlugin):
    title = "Duo Plugin - Multi Factor Authentication"
    slug = "duo-mfa"
    description = "Uses Duo to validate user actions with multi-factor authentication."
    version = duo_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = DuoConfiguration

    def send_push_notification(
        *,
        self,
        username: str,
        device: str = "auto",
        type: Optional[str],
        ipaddr: Optional[str] = None,
        hostname: Optional[str] = None,
        _async: Optional[int] = None,
    ):
        """Create a new push notification for authentication."""
        duo_client = duo_service.create_duo_auth_client(self.configuration)
        duo_client.auth(
            factor="push",
            username=username,
            ipaddr=ipaddr,
            hostname=hostname,
            async_txn=_async,
            type=type,
            device=device,
        )
