import logging

from starlette.config import Config


log = logging.getLogger(__name__)


config = Config(".env")

METAFLOW_NAMESPACE = config("METAFLOW_NAMESPACE", default=None)
