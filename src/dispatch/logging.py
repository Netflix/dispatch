import logging
from dispatch.config import LOG_LEVEL


def configure_logging():
    level = LOG_LEVEL.upper()
    if level == "DEBUG":
        # log level:logged message:full module path:function invoked:line number of logging call
        LOGFORMAT = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
        logging.basicConfig(level=level, format=LOGFORMAT)
    else:
        logging.basicConfig(level=level)
