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
from dispatch.signal.models import SignalInstanceCreate
from dispatch.plugins.dispatch_aws.config import AWSSQSConfiguration

from . import __version__

log = logging.getLogger(__name__)


class AWSSQSSignalConsumerPlugin(SignalConsumerPlugin):
    title = "AWS SQS - Signal Consumer"
    slug = "aws-sqs-signal-consumer"
    description = "Uses sqs to consume signals"
    version = __version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = AWSSQSConfiguration

    def consume(self, db_session, project):
        client = boto3.client("sqs", region_name=self.configuration.region)
        queue_url: str = client.get_queue_url(
            QueueName=self.configuration.queue_name,
            QueueOwnerAWSAccountId=self.configuration.queue_owner,
        )["QueueUrl"]

        while True:
            response = client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=self.configuration.batch_size,
                VisibilityTimeout=40,
                WaitTimeSeconds=20,
            )
            if response.get("Messages") and len(response.get("Messages")) > 0:
                entries = []
                for message in response["Messages"]:
                    body = json.loads(message["Body"])
                    signal_data = json.loads(body["Message"])

                    signal_instance = signal_service.create_signal_instance(
                        db_session=db_session,
                        signal_instance_in=SignalInstanceCreate(
                            project=project, raw=signal_data, **signal_data
                        ),
                    )
                    metrics_provider.counter(
                        "aws-sqs-signal-consumer.signal.received",
                        tags={
                            "signalName": signal_instance.signal.name,
                            "externalId": signal_instance.signal.external_id,
                        },
                    )
                    log.debug(
                        f"Received signal: SignalName: {signal_instance.signal.name} ExernalId: {signal_instance.signal.external_id}"
                    )
                    entries.append(
                        {"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]}
                    )
                if entries:
                    client.delete_message_batch(QueueUrl=queue_url, Entries=entries)
