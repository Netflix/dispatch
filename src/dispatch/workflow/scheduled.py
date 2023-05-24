import logging

from schedule import every
from sqlalchemy.orm import Session

from dispatch.decorators import scheduled_project_task, timer
from dispatch.messaging.strings import (
    INCIDENT_WORKFLOW_COMPLETE_NOTIFICATION,
    INCIDENT_WORKFLOW_UPDATE_NOTIFICATION,
)
from dispatch.plugin import service as plugin_service
from dispatch.plugin.models import PluginInstance
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.workflow import service as workflow_service

from .enums import WorkflowInstanceStatus
from .flows import send_workflow_notification
from .models import WorkflowInstance, WorkflowInstanceUpdate

log = logging.getLogger(__name__)

WORKFLOW_SYNC_INTERVAL = 30  # seconds


def sync_workflow(
    db_session: Session,
    project: Project,
    workflow_plugin: PluginInstance,
    instance: WorkflowInstance,
    notify: bool = False,
):
    """Performs workflow sync."""
    log.debug(
        f"Processing workflow instance. Instance: {instance.parameters} Workflow: {instance.workflow.name}"
    )
    instance_data = workflow_plugin.instance.get_workflow_instance(
        workflow_id=instance.workflow.resource_id,
        tags=[f"workflowId:{instance.workflow.resource_id}", f"workflowInstanceId:{instance.id}"],
    )

    log.debug(f"Retrieved instance data from plugin. Data: {instance_data}")

    # might add to try more retry logic instead of just failing.
    if not instance_data:
        log.warning(
            f"Unabled to sync instance data. WorkflowId: {instance.workflow.resource_id} WorkflowInstanceId: {instance.id}"
        )
        return

    instance_status_old = instance.status

    # add project information to artifacts
    for a in instance_data["artifacts"]:
        a["project"] = {"id": project.id, "name": project.name}

    instance = workflow_service.update_instance(
        db_session=db_session,
        instance=instance,
        instance_in=WorkflowInstanceUpdate(**instance_data),
    )

    # TODO extend notification to cases as required
    if notify and instance.incident:
        if instance_status_old != instance.status:
            if instance.status == WorkflowInstanceStatus.completed:
                send_workflow_notification(
                    project.id,
                    instance.incident.conversation.channel_id,
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
                    instance.incident.conversation.channel_id,
                    INCIDENT_WORKFLOW_UPDATE_NOTIFICATION,
                    db_session,
                    instance_status_old=instance_status_old,
                    instance_status_new=instance.status,
                    instance_weblink=instance.weblink,
                    instance_creator_name=instance.creator.individual.name,
                    workflow_name=instance.workflow.name,
                    workflow_description=instance.workflow.description,
                )


@scheduler.add(every(WORKFLOW_SYNC_INTERVAL).seconds, name="sync-workflows")
@timer
@scheduled_project_task
def sync_workflows(db_session: Session, project: Project):
    """Syncs all workflows."""
    workflow_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project.id, plugin_type="workflow"
    )

    if not workflow_plugin:
        log.warning(
            f"Workflows not synced. No workflow plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    workflow_instances = workflow_service.get_running_instances(
        db_session=db_session, project_id=project.id
    )
    for instance in workflow_instances:
        sync_workflow(db_session, project, workflow_plugin, instance)
