import logging

from schedule import every
from dispatch.database.core import SessionLocal

from dispatch.decorators import scheduled_project_task
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.messaging.strings import (
    INCIDENT_MONITOR_UPDATE_NOTIFICATION,
)
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.monitor import service as monitor_service


log = logging.getLogger(__name__)

MONITOR_SYNC_INTERVAL = 30  # seconds


def run_monitors(db_session, project, monitor_plugin, incidents, notify: bool = False):
    """Performs monitor run."""
    for incident in incidents:
        for instance in incident.monitor_instances:
            # once an instance is complete we don't update it any more
            if not instance.enabled:
                continue

            log.debug(f"Processing monitor instance. Instance: {instance.parameters}")
            instance_data = monitor_plugin.instance.get_match_status(
                monitor_id=instance.monitor.resource_id,
                monitor_instance_id=instance.id,
                incident_name=incident.name,
                incident_id=incident.id,
            )

            log.debug(f"Retrieved instance data from plugin. Data: {instance_data}")
            if not instance_data:
                log.warning(
                    f"Could not locate a Dispatch instance for a given workflow instance. WorkflowId: {instance.workflow.resource_id} WorkflowInstanceId: {instance.id} IncidentName: {incident.name}"
                )
                continue

            instance_status_old = instance.status

            instance = monitor_service.update_instance(
                db_session=db_session,
                instance=instance,
                instance_in=MonitorInstanceUpdate(**instance_data),
            )

            if notify:
                send_monitor_notification(
                    project.id,
                    incident.conversation.channel_id,
                    INCIDENT_MONITOR_UPDATE_NOTIFICATION,
                    db_session,
                    instance_status_old=instance_status_old,
                    instance_status_new=instance.status,
                    instance_weblink=instance.weblink,
                    instance_creator_name=instance.creator.individual.name,
                    monitor_name=instance.monitor.name,
                    monitor_description=instance.monitor.description,
                )


@scheduler.add(every(MONITOR_SYNC_INTERVAL).seconds, name="incident-workflow-sync")
@scheduled_project_task
def sync_active_stable_workflows(db_session: SessionLocal, project: Project):
    """Syncs incident workflows."""
    monitor_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="monitor"
    )
    if not monitor_plugin:
        log.warning(f"No monitor plugin is enabled. ProjectId: {project.id}")
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
