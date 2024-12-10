"""
.. module: dispatch.plugins.dispatchaws.plugin
    :platform: Unix
    :copyright: (c) 2023 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""

import base64
import json
import logging
import zlib
from typing import TypedDict

import boto3
from psycopg2.errors import UniqueViolation
from pydantic import ValidationError
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


def decompress_json(compressed_str: str) -> str:
    """Decompress a base64 encoded zlibed JSON string."""
    decoded = base64.b64decode(compressed_str)
    decompressed = zlib.decompress(decoded)
    return decompressed.decode("utf-8")


class SqsEntries(TypedDict):
    Id: str
    ReceiptHandle: str


class AWSSQSSignalConsumerPlugin(SignalConsumerPlugin):
    title = "AWS SQS - Signal Consumer"
    slug = "aws-sqs-signal-consumer"
    description = "Uses SQS to consume signals."
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
                log.info("No messages received from SQS.")
                continue

            entries: list[SqsEntries] = []
            for message in response["Messages"]:
                message_body = json.loads(message["Body"])
                message_body_message = message_body.get("Message")
                message_attributes = message_body.get("MessageAttributes", {})

                if message_attributes.get("compressed", {}).get("Value") == "zlib":
                    # Message is compressed, decompress it
                    message_body_message = decompress_json(message_body_message)
                    signal_data = json.loads(message_body_message)
                else:
                    signal_data = message_body_message

                try:
                    signal_instance_in = SignalInstanceCreate(
                        project=project, raw=signal_data, **signal_data
                    )
                except ValidationError as e:
                    log.warning(
                        f"Received a signal instance that does not conform to the `SignalInstanceCreate` structure. Skipping creation: {e}"
                    )
                    continue

                # if the signal has an existing uuid we check if it already exists
                if signal_instance_in.raw and signal_instance_in.raw.get("id"):
                    if signal_service.get_signal_instance(
                        db_session=db_session, signal_instance_id=signal_instance_in.raw["id"]
                    ):
                        log.info(
                            f"Received a signal instance that already exists in the database. Skipping creation: {signal_instance_in.raw['id']}"
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
                            f"Received a signal instance that already exists in the database. Skipping creation: {e}"
                        )
                    else:
                        log.exception(
                            f"Encountered an Integrity error when trying to create a signal instance: {e}"
                        )
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
                        f"Received a signal with name {signal_instance.signal.name} and id {signal_instance.signal.id}"
                    )
                    entries.append(
                        {"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]}
                    )

            if entries:
                client.delete_message_batch(QueueUrl=queue_url, Entries=entries)
