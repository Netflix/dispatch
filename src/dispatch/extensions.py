import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from .config import SENTRY_DSN, ENV


log = logging.getLogger(__file__)

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)


def configure_extensions():
    log.debug("Configuring extensions...")
    if SENTRY_DSN:
        sentry_sdk.init(dsn=str(SENTRY_DSN), integrations=[sentry_logging], environment=ENV)
