"""
.. module: dispatch.plugins.dispatch_aws.plugin
    :platform: Unix
    :license: Apache, see LICENSE for more details.
"""
import logging
from pydantic import Field

import boto3
from dispatch.config import BaseConfigurationModel

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_aws as aws_plugin
from dispatch.plugins.bases import SignalConsumerPlugin

log = logging.getLogger(__name__)


class AWSSQSConfiguration(BaseConfigurationModel):
    queue_url: str = Field(title="Queue to pull from.")
    wait_seconds: int = Field(
        title="Number of seconds to wait before returning an empty message.", default=10
    )


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
        self.configuration_schema = AWSSQSConfiguration

    def consume(self):
        """Consumes a message from a specified SQS queue."""
        sqs = boto3.client("sqs")
        response = sqs.receive_message(
            QueryUrl=self.configuration.queue_name,
            AttributeNames=["SentTimestamp"],
            MessageAttributeNames=["All"],
            WaitTimeSeconds=self.configuration.wait_seconds,
        )
        return response
