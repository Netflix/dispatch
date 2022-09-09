"""
.. module: dispatch.plugins.dispatch_aws.plugin
    :platform: Unix
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_aws as aws_plugin
from dispatch.plugins.bases import SignalConsumerPlugin

from .config import AWSConfiguration

log = logging.getLogger(__name__)


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class AWSSQSSignalConsumerPlugin(SignalConsumerPlugin):
    title = "AWS SQS Plugin - Signal consumer"
    slug = "aws-sqs-signal-consumer"
    description = "Uses a AWS SQS queue as a signal enrichment source."
    version = aws_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = AWSConfiguration

    def consume(self):
        """Enriches an event."""
        return {}
