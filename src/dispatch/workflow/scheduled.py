import logging

from schedule import every
from dispatch.database.core import SessionLocal

from dispatch.decorators import scheduled_project_task
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.messaging.strings import (
    INCIDENT_WORKFLOW_COMPLETE_NOTIFICATION,
    INCIDENT_WORKFLOW_UPDATE_NOTIFICATION,
)
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.workflow import service as workflow_service

from .enums import WorkflowInstanceStatus
from .flows import send_workflow_notification
from .models import WorkflowInstanceUpdate


log = logging.getLogger(__name__)

WORKFLOW_SYNC_INTERVAL = 30  # seconds


def sync_workflows(db_session, project, workflow_plugin, incidents, notify: bool = False):
    """Performs workflow sync."""
    for incident in incidents:
        for instance in incident.workflow_instances:
            # once an instance is complete we don't update it any more
            if instance.status == WorkflowInstanceStatus.completed:
                continue

            log.debug(
                f"Processing workflow instance. Instance: {instance.parameters} Workflow: {instance.workflow.name}"
            )
            instance_data = workflow_plugin.instance.get_workflow_instance(
                workflow_id=instance.workflow.resource_id,
                workflow_instance_id=instance.id,
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

            instance = workflow_service.update_instance(
                db_session=db_session,
                instance=instance,
                instance_in=WorkflowInstanceUpdate(**instance_data),
            )

            if notify:
                if instance_status_old != instance.status:
                    if instance.status == WorkflowInstanceStatus.completed:
                        send_workflow_notification(
                            project.id,
                            incident.conversation.channel_id,
                            INCIDENT_WORKFLOW_COMPLETE_NOTIFICATION,
                            db_session,
                            instance_status_old=instance_status_old,
                            instance_status_new=instance.status,
                            instance_weblink=instance.weblink,
                            instance_creator_name=instance.creator.individual.name,
                            instance_artifacts=instance.artifacts,
                            workflow_name=instance.workflow.name,
                            workflow_description=instance.workflow.description,
                        )
                    else:
                        send_workflow_notification(
                            project.id,
                            incident.conversation.channel_id,
                            INCIDENT_WORKFLOW_UPDATE_NOTIFICATION,
                            db_session,
                            instance_status_old=instance_status_old,
                            instance_status_new=instance.status,
                            instance_weblink=instance.weblink,
                            instance_creator_name=instance.creator.individual.name,
                            workflow_name=instance.workflow.name,
                            workflow_description=instance.workflow.description,
                        )


@scheduler.add(every(WORKFLOW_SYNC_INTERVAL).seconds, name="incident-workflow-sync")
@scheduled_project_task
def sync_active_stable_workflows(db_session: SessionLocal, project: Project):
    """Syncs incident workflows."""
    workflow_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="workflow"
    )
    if not workflow_plugin:
        log.warning(f"No workflow plugin is enabled. ProjectId: {project.id}")
        return

    # we get all active and stable incidents
    active_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.active
    )
    stable_incidents = incident_service.get_all_by_status(
        db_session=db_session, project_id=project.id, status=IncidentStatus.stable
    )
    incidents = active_incidents + stable_incidents
    sync_workflows(db_session, project, workflow_plugin, incidents, notify=True)


@scheduler.add(every(1).day, name="incident-workflow-daily-sync")
@scheduled_project_task
def daily_sync_workflow(db_session: SessionLocal, project: Project):
    """Syncs all incident workflows daily."""
    workflow_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="workflow"
    )
    if not workflow_plugin:
        log.warning(f"No workflow plugin is enabled. ProjectId: {project.id}")
        return

    incidents = incident_service.get_all(db_session=db_session, project_id=project.id).all()
    sync_workflows(db_session, project, workflow_plugin, incidents, notify=False)
