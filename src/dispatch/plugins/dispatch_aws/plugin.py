"""
.. module: dispatch.plugins.dispatchaws.plugin
    :platform: Unix
    :copyright: (c) 2023 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import boto3
import json
import logging

from dispatch.metrics import provider as metrics_provider
from dispatch.plugins.bases import SignalConsumerPlugin
from dispatch.signal import service as signal_service
from dispatch.signal.models import SignalInstance
from dispatch.plugins.dispatch_aws.config import AWSSQSConfigurationSchema

from . import __version__

log = logging.getLogger(__name__)


class SQSSignalConsumerPlugin(SignalConsumerPlugin):
    title = "AWS SQS - Signal Consumer"
    slug = "aws-sqs-signal-consumer"
    description = "Uses sqs to consume signals"
    version = __version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = AWSSQSConfigurationSchema

    def consume(
        self,
    ):
        client = boto3.client("sqs", region_name=self.configuration.region)
        sqs_queue_url: str = client.get_queue_url(
            QueueName=self.configuration.queue_name, QueueOwnerAWSAccountId=self.sqs_queue_owner
        )["QueueUrl"]

        while True:
            response = client.receive_message(
                QueueUrl=sqs_queue_url,
                MaxNumberOfMessages=self.configuration.batch_size,
                VisibilityTimeout=2 * self.round_length,
                WaitTimeSeconds=self.round_length,
            )
            if response.get("Messages") and len(response.get("Messages")) > 0:
                entries = []
                for message in response["Messages"]:
                    try:
                        body = json.loads(message["Body"])
                        signal = signal_service.create_signal_instance(SignalInstance(**body))
                        metrics_provider.counter(
                            "sqs.signal.received", tags={"signalName": signal.name}
                        )
                        log.debug(f"Received signal: {signal}")
                        entries.append(
                            {"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]}
                        )
                    except Exception as e:
                        log.exception(e)

                client.delete_message_batch(QueueUrl=sqs_queue_url, Entries=entries)
