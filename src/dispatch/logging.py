import logging

from dispatch.config import LOG_LEVEL
from dispatch.enums import LogLevels


DEFAULT_LOG_LEVEL = LogLevels.error
LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


def configure_logging():
    log_level = str(LOG_LEVEL).upper()  # cast to string
    log_levels = [level for level in LogLevels]

    if log_level not in log_levels:
        # we use the default log level
        logging.basicConfig(level=DEFAULT_LOG_LEVEL)
        return

    if log_level == LogLevels.debug:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
        return

    logging.basicConfig(level=log_level)
