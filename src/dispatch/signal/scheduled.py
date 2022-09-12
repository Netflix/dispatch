"""
.. module: dispatch.signal.scheduled
    :platform: Unix
    :copyright: (c) 2022 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from schedule import every

from dispatch.database.core import SessionLocal
from dispatch.scheduler import scheduler
from dispatch.project.models import Project
from dispatch.plugin import service as plugin_service
from dispatch.signal import flows as signal_flows
from dispatch.decorators import scheduled_project_task
from dispatch.signal.models import SignalCreate

log = logging.getLogger(__name__)


# TODO do we want per signal source flexibility?
@scheduler.add(every(5).minutes, name="signal-consume")
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
        signals = plugin.instance.consume()

        for signal in signals:
            from pprint import pprint

            pprint(signal)
            signal_in = SignalCreate(**signal, project=project)
            signal_flows.create_signal(db_session=db_session, signal_in=signal_in)
