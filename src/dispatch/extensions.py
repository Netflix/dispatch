import logging

import sentry_sdk
from .config import SENTRY_DSN

from sentry_sdk.integrations.logging import LoggingIntegration

sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)


def configure_extensions():
    if SENTRY_DSN:
        sentry_sdk.init(dsn=str(SENTRY_DSN), integrations=[sentry_logging])
