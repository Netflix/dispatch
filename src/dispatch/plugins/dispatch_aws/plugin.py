"""
.. module: dispatch.plugins.dispatchaws.plugin
    :platform: Unix
    :copyright: (c) 2023 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""

import json
import logging
from typing import TypedDict

import boto3
from pydantic import ValidationError
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dispatch.metrics import provider as metrics_provider
from dispatch.plugins.bases import SignalConsumerPlugin
from dispatch.plugins.dispatch_aws.config import AWSSQSConfiguration
from dispatch.project.models import Project
from dispatch.signal import service as signal_service
from dispatch.signal.models import SignalInstanceCreate

from . import __version__

log = logging.getLogger(__name__)


class SqsEntries(TypedDict):
    Id: str
    ReceiptHandle: str


class AWSSQSSignalConsumerPlugin(SignalConsumerPlugin):
    title = "AWS SQS - Signal Consumer"
    slug = "aws-sqs-signal-consumer"
    description = "Uses sqs to consume signals"
    version = __version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = AWSSQSConfiguration

    def consume(self, db_session: Session, project: Project) -> None:
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
            if not response.get("Messages") or len(response["Messages"]) == 0:
                log.info("No messages received from SQS")
                continue

            entries: list[SqsEntries] = []
            for message in response["Messages"]:
                body = json.loads(message["Body"])
                signal_data = json.loads(body["Message"])
                try:
                    signal_instance_in = SignalInstanceCreate(
                        project=project, raw=signal_data, **signal_data
                    )
                except ValidationError as e:
                    log.warning(
                        f"Received signal instance that does not conform to `SignalInstanceCreate` structure, skipping creation: {e}"
                    )
                    continue

                try:
                    with db_session.begin_nested():
                        signal_instance = signal_service.create_signal_instance(
                            db_session=db_session,
                            signal_instance_in=signal_instance_in,
                        )
                except IntegrityError as e:
                    if isinstance(e.orig, UniqueViolation):
                        log.info(
                            f"Received signal instance that already exists in the database, skipping creation: {e}"
                        )
                    else:
                        log.exception(f"Integrity error when creating signal instance: {e}")
                    continue
                except Exception as e:
                    log.exception(f"Unable to create signal instance: {e}")
                    db_session.rollback()
                    continue
                else:
                    metrics_provider.counter(
                        "aws-sqs-signal-consumer.signal.received",
                        tags={
                            "signalName": signal_instance.signal.name,
                            "externalId": signal_instance.signal.external_id,
                        },
                    )
                    log.debug(
                        f"Received signal: name: {signal_instance.signal.name} id: {signal_instance.signal.id}"
                    )
                    entries.append(
                        {"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]}
                    )

            if entries:
                client.delete_message_batch(QueueUrl=queue_url, Entries=entries)
