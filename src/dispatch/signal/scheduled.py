"""
.. module: dispatch.signal.scheduled
    :platform: Unix
    :copyright: (c) 2022 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from datetime import datetime, timedelta, timezone
import logging
import queue
from sqlalchemy import asc
from sqlalchemy.orm import scoped_session

from schedule import every
from dispatch.database.core import SessionLocal, sessionmaker, engine
from dispatch.scheduler import scheduler
from dispatch.project.models import Project
from dispatch.plugin import service as plugin_service
from dispatch.signal import flows as signal_flows
from dispatch.decorators import scheduled_project_task, timer
from dispatch.signal.models import SignalInstance

log = logging.getLogger(__name__)


# TODO do we want per signal source flexibility?
@scheduler.add(every(1).minutes, name="signal-consume")
@scheduled_project_task
def consume_signals(db_session: SessionLocal, project: Project):
    """Consume signals from external sources."""
    plugins = plugin_service.get_active_instances(
        db_session=db_session, plugin_type="signal-consumer", project_id=project.id
    )

    if not plugins:
        log.debug(
            f"No active plugins were found. PluginType: 'signal-consumer' ProjectId: {project.id}"
        )
        return

    for plugin in plugins:
        log.debug(f"Consuming signals. Signal Consumer: {plugin.plugin.slug}")
        signal_instances = plugin.instance.consume()
        for signal_instance_data in signal_instances:
            log.info(f"Attempting to process the following signal: {signal_instance_data['id']}")
            try:
                signal_flows.create_signal_instance(
                    db_session=db_session,
                    project=project,
                    signal_instance_data=signal_instance_data,
                )
            except Exception as e:
                log.debug(signal_instance_data)
                log.exception(e)


@timer
def process_signal_instance(db_session: SessionLocal, signal_instance: SignalInstance) -> None:
    try:
        signal_flows.signal_instance_create_flow(
            db_session=db_session,
            signal_instance_id=signal_instance.id,
        )
    except Exception as e:
        log.debug(signal_instance)
        log.exception(e)
    finally:
        db_session.close()


MAX_SIGNAL_INSTANCES = 500
signal_queue = queue.Queue(maxsize=MAX_SIGNAL_INSTANCES)


@timer
@scheduler.add(every(1).minutes, name="signal-process")
@scheduled_project_task
def process_signals(db_session: SessionLocal, project: Project):
    """
    Process signals and create cases if appropriate.

    This function processes signals within a given project, creating cases if necessary.
    It runs every minute, processing signals that meet certain criteria within the last 5 minutes.
    Signals are added to a queue for processing, and then each signal instance is processed.

    Args:
        db_session: The database session used to query and update the database.
        project: The project for which the signals will be processed.

    Notes:
        The function is decorated with three decorators:
            - scheduler.add: schedules the function to run every minute.
            - scheduled_project_task: ensures that the function is executed as a scheduled project task.

        The function uses a queue to process signal instances in a first-in-first-out (FIFO) order
        This ensures that signals are processed in the order they were added to the queue.

        A scoped session is used to create a new database session for each signal instance
        This ensures that each signal instance is processed using its own separate database connection,
        preventing potential issues with concurrent connections.
    """
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    signal_instances = (
        (
            db_session.query(SignalInstance)
            .filter(SignalInstance.project_id == project.id)
            .filter(SignalInstance.filter_action == None)  # noqa
            .filter(SignalInstance.case_id == None)  # noqa
            .filter(SignalInstance.created_at >= one_hour_ago)
        )
        .order_by(asc(SignalInstance.created_at))
        .limit(MAX_SIGNAL_INSTANCES)
    )
    # Add each signal_instance to the queue for processing
    for signal_instance in signal_instances:
        signal_queue.put(signal_instance)

    schema_engine = engine.execution_options(
        schema_translate_map={
            None: "dispatch_organization_default",
        }
    )
    session = scoped_session(sessionmaker(bind=schema_engine))

    # Process each signal instance in the queue
    while not signal_queue.empty():
        signal_instance = signal_queue.get()
        db_session = session()
        process_signal_instance(db_session, signal_instance)
