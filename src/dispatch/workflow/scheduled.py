import logging

from schedule import every

from dispatch.decorators import background_task
from dispatch.messaging import (
    INCIDENT_WORKFLOW_UPDATE_NOTIFICATION,
    INCIDENT_WORKFLOW_COMPLETE_NOTIFICATION,
)

from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack.modals import workflow_service
from dispatch.scheduler import scheduler
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from .models import WorkflowInstanceStatus, WorkflowInstanceUpdate
from .flows import send_workflow_notification

log = logging.getLogger(__name__)

WORKFLOW_SYNC_INTERVAL = 30  # seconds


def sync_workflows(db_session, incidents, notify: bool = False):
    """Performs workflow sync."""
    p = plugin_service.get_active(db_session=db_session, plugin_type="workflow")
    for incident in incidents:
        for instance in incident.workflow_instances:

            log.debug(
                f"Processing workflow instance. Instance: {instance.parameters} Workflow: {instance.workflow.name}"
            )
            instances = p.instance.get_workflow_instances(workflow_id=instance.workflow.resource_id)

            # create or update known instances
            for instance_data in instances:
                if not instance_data["instance_id"]:
                    log.warning(
                        f"Could not locate a Dispatch instance for a given workflow instance. InstanceData: {instance_data}"
                    )
                    continue

                current_instance = workflow_service.get_instance(
                    db_session=db_session, instance_id=int(instance_data["instance_id"])
                )

                if not current_instance:
                    log.warning(
                        f"Could not locate a Dispatch instance for a given workflow instance. InstanceData: {instance_data}"
                    )
                    continue

                instance_status_old = current_instance.status

                updated_instance = workflow_service.update_instance(
                    db_session=db_session,
                    instance=instance,
                    instance_in=WorkflowInstanceUpdate(**instance_data),
                )

                instance_status_new = updated_instance.status

                if notify:
                    if instance_status_old != instance_status_new:
                        if instance_status_new == WorkflowInstanceStatus.completed.value:
                            send_workflow_notification(
                                incident.conversation.channel_id,
                                INCIDENT_WORKFLOW_COMPLETE_NOTIFICATION,
                                instance.artifacts,
                            )
                        else:
                            send_workflow_notification(
                                incident.conversation.channel_id,
                                INCIDENT_WORKFLOW_UPDATE_NOTIFICATION,
                                instance_status_old,
                                instance_status_new,
                                instance.weblink,
                                instance.creator.individual.name,
                                instance.workflow.name,
                                instance.workflow.description,
                                db_session,
                            )


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
