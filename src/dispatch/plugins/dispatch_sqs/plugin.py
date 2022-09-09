"""
.. module: dispatch.plugins.dispatch_sqs.plugin
    :platform: Unix
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_sqs as sqs_plugin
from dispatch.plugins.bases import SignalConsumerPlugin

from .config import SQSConfiguration

log = logging.getLogger(__name__)


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class SQSSignalConsumerPlugin(SignalConsumerPlugin):
    title = "SQS Plugin - Signal Consumer"
    slug = "aws-signal-consumer"
    description = "Uses SQS as a signal source."
    version = sqs_plugin.__version__

    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = SQSConfiguration

    def consume(
        self, name: str, description: str = None, title: str = None, participants: List[str] = []
    ):
        """Consumes an event."""
        return {}
