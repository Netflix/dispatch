"""
.. module: dispatch.auth.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from starlette.requests import Request
from dispatch.plugins.base import plugins
from dispatch.config import (
    DISPATCH_AUTHENTICATION_PROVIDER_SLUG,
    DISPATCH_AUTHENTICATION_DEFAULT_USER,
)

log = logging.getLogger(__name__)


def get_current_user(*, request: Request):
    """Attempts to get the current user depending on the configured authentication provider."""
    if DISPATCH_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
        return auth_plugin.get_current_user(request)
    else:
        log.warning(
            "No authentication provider has been provided. There is currently no user authentication."
        )
        return DISPATCH_AUTHENTICATION_DEFAULT_USER
