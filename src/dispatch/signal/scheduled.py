"""
.. module: dispatch.signal.scheduled
    :platform: Unix
    :copyright: (c) 2022 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from schedule import every
from threading import Lock
from collections import deque

from dispatch.database.core import SessionLocal
from dispatch.scheduler import scheduler
from dispatch.project.models import Project
from dispatch.plugin import service as plugin_service
from dispatch.signal import flows as signal_flows
from dispatch.decorators import scheduled_project_task

log = logging.getLogger(__name__)

lock = Lock()
signal_deque = deque()


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
            try:
                # Add the signal instance and db_session to the deque
                signal_deque.append((db_session, project, signal_instance_data))

            except Exception as e:
                log.debug(signal_instance_data)
                log.exception(e)

    # Process the signal instances in the deque
    _process_signal_deque()


def _process_signal_deque() -> None:
    while True:
        with lock:
            if not signal_deque:
                break
            db_session, project, signal_instance_data = signal_deque.popleft()
            log.info(f"Attempting to process the following signal: {signal_instance_data['id']}")
            try:
                signal_flows.create_signal_instance(
                    db_session=db_session,
                    project=project,
                    signal_instance_data=signal_instance_data,
                )
            except Exception as e:
                log.exception(e)
