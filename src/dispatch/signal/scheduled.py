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

        if signal_instances:
            plugin.instance.delete()


@scheduler.add(every(1).minutes, name="signal-process")
@scheduled_project_task
def process_signals(db_session: SessionLocal, project: Project):
    """Processes signals and create cases if appropriate."""
    signal_instances = (
        db_session.query(SignalInstance)
        .filter(SignalInstance.project_id == project.id)
        .filter(SignalInstance.filter_action == None)  # noqa
        .filter(SignalInstance.case_id == None)  # noqa
    ).limit(100)
    for signal_instance in signal_instances:
        log.info(f"Attempting to process the following signal: {signal_instance.id}")
        try:
            signal_flows.signal_instance_create_flow(
                db_session=db_session,
                signal_instance_id=signal_instance.id,
            )
        except Exception as e:
            log.debug(signal_instance)
            log.exception(e)
