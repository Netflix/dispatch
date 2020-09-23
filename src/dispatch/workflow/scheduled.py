import logging

from schedule import every

from dispatch.decorators import background_task
from dispatch.plugin import service as plugin_service
from dispatch.scheduler import scheduler
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from .models import WorkflowInstanceStatus

log = logging.getLogger(__name__)

WORKFLOW_SYNC_INTERVAL = 30  # seconds


def sync_workflows(db_session, incidents, notify: bool = False):
    """Performs workflow sync."""
    p = plugin_service.get_active(db_session=db_session, plugin_type="workflow")
    for incident in incidents:
        for workflow in incident.workflows:
            log.debug(f"Processing workflow. Name: {workflow.id}")
            for instance in workflow.instances:
                if instance.status != WorkflowInstanceStatus.completed.value:
                    log.debug(f"Updating workflow instance. InstanceId: {instance.resource_id}")
                    data = p.get_instance(workflow.resource_id, instance.resource_id)
                    log.debug(f"Instance Data: {data}")


@scheduler.add(every(WORKFLOW_SYNC_INTERVAL).seconds, name="incident-workflow-sync")
@background_task
def sync_active_stable_workflows(db_session=None):
    """Syncs incident workflows."""
    # we get all active and stable incidents
    active_incidents = incident_service.get_all_by_status(
        db_session=db_session, status=IncidentStatus.active
    )
    stable_incidents = incident_service.get_all_by_status(
        db_session=db_session, status=IncidentStatus.stable
    )
    incidents = active_incidents + stable_incidents
    sync_workflows(db_session, incidents, notify=True)


@scheduler.add(every(1).day, name="incident-workflow-daily-sync")
@background_task
def daily_sync_workflow(db_session=None):
    """Syncs all incident workflows daily."""
    incidents = incident_service.get_all(db_session=db_session).all()
    sync_workflows(db_session, incidents, notify=False)
