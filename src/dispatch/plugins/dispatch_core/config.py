import logging

from starlette.config import Config


log = logging.getLogger(__name__)


config = Config(".env")
