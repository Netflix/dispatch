import logging

from schedule import every

from dispatch.database.core import SessionLocal, resolve_attr
from dispatch.decorators import scheduled_project_task, timer
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.messaging.strings import (
    INCIDENT_MONITOR_UPDATE_NOTIFICATION,
)
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.monitor.models import MonitorUpdate
from dispatch.monitor import service as monitor_service
from dispatch.monitor.flows import send_monitor_notification


log = logging.getLogger(__name__)

MONITOR_SYNC_INTERVAL = 30  # seconds


def run_monitors(db_session, project, monitor_plugin, incidents, notify: bool = False):
    """Performs monitor run."""
    for incident in incidents:
        for monitor in incident.monitors:
            # once an instance is complete we don't update it any more
            if not monitor.enabled:
                continue

            log.debug(f"Processing monitor. Monitor: {monitor.weblink}")
            monitor_status = monitor_plugin.instance.get_match_status(
                weblink=monitor.weblink,
                last_modified=monitor.updated_at,
            )

            log.debug(f"Retrieved data from plugin. Data: {monitor_status}")
            if not monitor_status:
                continue

            monitor_status_old = monitor.status
            if monitor_status["state"] == monitor.status["state"]:
                continue

            monitor_service.update(
                db_session=db_session,
                monitor=monitor,
                monitor_in=MonitorUpdate(
                    id=monitor.id,
                    weblink=monitor.weblink,
                    enabled=monitor.enabled,
                    status=monitor_status,
                ),
            )

            if notify:
                send_monitor_notification(
                    project.id,
                    incident.conversation.channel_id,
                    INCIDENT_MONITOR_UPDATE_NOTIFICATION,
                    db_session,
                    monitor_state_old=monitor_status_old["state"],
                    monitor_state_new=monitor.status["state"],
                    weblink=monitor.weblink,
                    monitor_creator_name=resolve_attr(monitor, "creator.individual.name"),
                )


@scheduler.add(every(MONITOR_SYNC_INTERVAL).seconds, name="sync-active-stable-monitors")
@timer
@scheduled_project_task
def sync_active_stable_monitors(db_session: SessionLocal, project: Project):
    """Syncs incident monitors for active and stable incidents."""
    monitor_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="monitor"
    )
    if not monitor_plugin:
        log.warning(
            f"Incident monitors not synced. No monitor plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    # we get all active and stable incidents
    active_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.active
    )
    stable_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.stable
    )
    incidents = active_incidents + stable_incidents
    run_monitors(db_session, project, monitor_plugin, incidents, notify=True)
