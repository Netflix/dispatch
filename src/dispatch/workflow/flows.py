from sqlalchemy.orm import Session

from dispatch.config import DISPATCH_UI_URL
from dispatch.decorators import background_task
from dispatch.plugin import service as plugin_service
from dispatch.signal.models import SignalInstance
from dispatch.workflow import service as workflow_serivce
from dispatch.workflow.models import Workflow, WorkflowInstance, WorkflowInstanceCreate


def send_workflow_notification(project_id, conversation_id, message_template, db_session, **kwargs):
    """Sends a workflow notification."""
    notification_text = "Incident Notification"
    notification_type = "incident-notification"

    plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="conversation", project_id=project_id
    )
    plugin.instance.send(
        conversation_id, notification_text, message_template, notification_type, **kwargs
    )


@background_task
def signal_workflow_run_flow(
    db_session: Session,
    workflow: Workflow,
    workflow_instance_in: WorkflowInstanceCreate,
    signal_instance: SignalInstance,
) -> WorkflowInstance:
    """Runs a workflow with the given parameters."""
    instance = workflow_serivce.create_instance(
        db_session=db_session,
        workflow=workflow,
        instance_in=WorkflowInstanceCreate(**workflow_instance_in.dict()),
    )
    entities = signal_instance.entities

    params = {}
    for p in workflow.parameters:
        if value := p.get("value"):
            for entity in entities:
                if entity.entity_type.name == value:
                    params.update({p["key"]: entity.value})

    params.update(
        {
            "externalRef": f"{DISPATCH_UI_URL}/{instance.signal.project.organization.name}/signals/{instance.signal.name}?project={instance.signal.project.name}",
            "workflowInstanceId": instance.id,
        }
    )

    workflow.plugin_instance.instance.run(workflow.resource_id, params)

    return instance
