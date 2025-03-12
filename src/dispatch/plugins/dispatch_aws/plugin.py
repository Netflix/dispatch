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
import signal as os_signal
import time
import zlib
from typing import TypedDict

import boto3
from psycopg2.errors import UniqueViolation
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, ResourceClosedError
from sqlalchemy.orm import Session

from dispatch.database.core import get_session
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
        self._shutdown = False

    def _setup_signal_handlers(self):
        """Setup handlers for graceful shutdown."""

        def handle_shutdown(signum, frame):
            self._shutdown = True
            log.info("Received shutdown signal, finishing current batch before exiting...")

        # Handle graceful shutdown signals
        os_signal.signal(os_signal.SIGTERM, handle_shutdown)
        os_signal.signal(os_signal.SIGINT, handle_shutdown)

    def _process_message(
        self, db_session: Session, message: dict, project: Project
    ) -> SqsEntries | None:
        """Process a single SQS message and return entry for deletion if successful.

        Uses a nested transaction (SAVEPOINT) for message-level isolation within the batch transaction.
        If the message processing fails, only its SAVEPOINT is rolled back, not affecting other messages.

        Args:
            db_session: The SQLAlchemy session for database operations
            message: The SQS message to process
            project: The project context for the signal

        Returns:
            SqsEntries if message was processed successfully, None otherwise
        """
        try:
            message_body = json.loads(message["Body"])
            message_body_message = message_body.get("Message")
            message_attributes = message_body.get("MessageAttributes", {})

            if message_attributes.get("compressed", {}).get("Value") == "zlib":
                # Message is compressed, decompress it
                message_body_message = decompress_json(message_body_message)

            signal_data = json.loads(message_body_message)
        except Exception as e:
            log.exception(f"Unable to extract signal data from SQS message: {e}")
            return None

        try:
            signal_instance_in = SignalInstanceCreate(
                project=project, raw=signal_data, **signal_data
            )
        except ValidationError as e:
            log.warning(
                f"Received a signal instance that does not conform to the SignalInstanceCreate pydantic model. Skipping creation: {e}"
            )
            return None

        # if the signal has an existing uuid we check if it already exists
        if signal_instance_in.raw and signal_instance_in.raw.get("id"):
            if signal_service.get_signal_instance(
                db_session=db_session, signal_instance_id=signal_instance_in.raw["id"]
            ):
                log.info(
                    f"Received a signal that already exists in the database. Skipping signal instance creation: {signal_instance_in.raw['id']}"
                )
                return None

        try:
            with db_session.begin_nested():
                signal_instance = signal_service.create_signal_instance(
                    db_session=db_session,
                    signal_instance_in=signal_instance_in,
                )

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
                return {"Id": message["MessageId"], "ReceiptHandle": message["ReceiptHandle"]}

        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                log.info(
                    f"Received a signal that already exists in the database. Skipping signal instance creation: {e}"
                )
            else:
                log.exception(
                    f"Encountered an integrity error when trying to create a signal instance: {e}"
                )
            return None
        except (ResourceClosedError, Exception) as e:
            log.exception(
                f"Encountered an error when trying to create a signal instance. Signal name/variant: {signal_instance_in.raw['name'] if signal_instance_in.raw and signal_instance_in.raw['name'] else signal_instance_in.raw['variant']}. Error: {e}"
            )
            return None

    def consume(self, db_session: Session, project: Project) -> None:
        """Consume messages from SQS queue.

        Implements a long-running consumer with graceful shutdown handling.
        Uses the application's session management with nested transactions for message-level isolation.

        Args:
            db_session: Initial SQLAlchemy session (will be closed after setup)
            project: The project context for signal processing

        Note:
            - Uses dispatch's get_session() context manager for proper session lifecycle
            - Individual messages use nested transactions (SAVEPOINTs)
            - Handles SIGTERM/SIGINT for graceful shutdown
            - Includes automatic session tracking and cleanup
        """
        try:
            self._setup_signal_handlers()

            client = boto3.client("sqs", region_name=self.configuration.region)
            queue_url: str = client.get_queue_url(
                QueueName=self.configuration.queue_name,
                QueueOwnerAWSAccountId=self.configuration.queue_owner,
            )["QueueUrl"]

            # Close the original session as we'll use get_session()
            db_session.close()

            while not self._shutdown:
                try:
                    response = client.receive_message(
                        QueueUrl=queue_url,
                        MaxNumberOfMessages=self.configuration.batch_size,
                        # Increased visibility timeout to handle larger batches and potential delays
                        # 5 minutes should cover most processing scenarios while preventing
                        # excessive message lock time
                        VisibilityTimeout=300,  # 5 minutes
                        # Long polling wait time - reduces empty responses while allowing
                        # reasonable shutdown time
                        WaitTimeSeconds=20,
                    )

                    if not response.get("Messages"):
                        log.info("No messages received from SQS.")
                        continue

                    entries: list[SqsEntries] = []
                    with get_session() as batch_session:
                        # Batch transaction - commits all successful messages or none
                        with batch_session.begin():
                            for message in response["Messages"]:
                                if self._shutdown:
                                    log.info("Shutdown requested, stopping message processing...")
                                    break
                                entry = self._process_message(batch_session, message, project)
                                if entry:
                                    entries.append(entry)

                    # Only delete messages that were successfully processed
                    if entries:
                        client.delete_message_batch(QueueUrl=queue_url, Entries=entries)

                except Exception as e:
                    log.exception("Error processing message batch: %s", e)
                    if not self._shutdown:
                        time.sleep(1)  # Prevent tight error loops

        except Exception as e:
            log.exception("Fatal error in consumer: %s", e)
            raise
        finally:
            log.info("Consumer shutting down...")
            if db_session:
                db_session.close()
