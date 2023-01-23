from typing import List, Optional

from sqlalchemy.sql.expression import true
from dispatch.config import DISPATCH_UI_URL
from dispatch.project import service as project_service
from dispatch.plugin import service as plugin_service
from dispatch.incident import service as incident_service
from dispatch.case import service as case_service
from dispatch.participant import service as participant_service
from dispatch.document import service as document_service
from dispatch.workflow.enums import WorkflowInstanceStatus

from .models import (
    Workflow,
    WorkflowInstance,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowInstanceCreate,
    WorkflowInstanceUpdate,
)


def get(*, db_session, workflow_id: int) -> Optional[Workflow]:
    """Returns a workflow based on the given workflow id."""
    return db_session.query(Workflow).filter(Workflow.id == workflow_id).one_or_none()


def get_by_name(*, db_session, name: str) -> Optional[Workflow]:
    """Returns a workflow based on the given workflow name."""
    return db_session.query(Workflow).filter(Workflow.name == name).one_or_none()


def get_all(*, db_session) -> List[Optional[Workflow]]:
    """Returns all workflows."""
    return db_session.query(Workflow)


def get_enabled(*, db_session, project_id: int = None) -> List[Optional[Workflow]]:
    """Fetches all enabled workflows."""
    if project_id:
        return (
            db_session.query(Workflow)
            .filter(Workflow.enabled == true())
            .filter(Workflow.project_id == project_id)
            .all()
        )
    return db_session.query(Workflow).filter(Workflow.enabled == true()).all()


def create(*, db_session, workflow_in: WorkflowCreate) -> Workflow:
    """Creates a new workflow."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=workflow_in.project
    )
    plugin_instance = plugin_service.get_instance(
        db_session=db_session, plugin_instance_id=workflow_in.plugin_instance.id
    )
    workflow = Workflow(
        **workflow_in.dict(exclude={"plugin_instance", "project"}),
        plugin_instance=plugin_instance,
        project=project,
    )

    db_session.add(workflow)
    db_session.commit()
    return workflow


def update(*, db_session, workflow: Workflow, workflow_in: WorkflowUpdate) -> Workflow:
    """Updates a workflow."""
    workflow_data = workflow.dict()
    update_data = workflow_in.dict(skip_defaults=True, exclude={"plugin_instance"})

    for field in workflow_data:
        if field in update_data:
            setattr(workflow, field, update_data[field])

    plugin_instance = plugin_service.get_instance(
        db_session=db_session, plugin_instance_id=workflow_in.plugin_instance.id
    )

    workflow.plugin_instance = plugin_instance

    db_session.commit()
    return workflow


def delete(*, db_session, workflow_id: int):
    """Deletes a workflow."""
    db_session.query(Workflow).filter(Workflow.id == workflow_id).delete()
    db_session.commit()


def get_instance(*, db_session, instance_id: int) -> WorkflowInstance:
    """Fetches a workflow instance by its id."""
    return (
        db_session.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).one_or_none()
    )


def get_running_instances(*, db_session) -> List[WorkflowInstance]:
    """Fetches all running instances."""
    return (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.status.in_(
                (
                    WorkflowInstanceStatus.created,
                    WorkflowInstanceStatus.running,
                    WorkflowInstanceStatus.submitted,
                )
            )
        )
        .all()
    )


def create_instance(
    *, db_session, workflow, instance_in: WorkflowInstanceCreate
) -> WorkflowInstance:
    """Creates a new workflow instance."""
    instance = WorkflowInstance(
        **instance_in.dict(exclude={"incident", "case", "creator", "artifacts"})
    )

    if instance_in.incident:
        incident = incident_service.get(db_session=db_session, incident_id=instance_in.incident.id)
        instance.incident = incident

    if instance_in.case:
        case = case_service.get(db_session=db_session, case_id=instance_in.case.id)
        instance.case = case

    instance.workflow = workflow

    if instance_in.creator:
        creator = participant_service.get_by_incident_id_and_email(
            db_session=db_session,
            incident_id=incident.id,
            email=instance_in.creator.individual.email,
        )
        instance.creator = creator

    for a in instance_in.artifacts:
        artifact_document = document_service.create(db_session=db_session, document_in=a)
        instance.artifacts.append(artifact_document)

    db_session.add(instance)
    db_session.commit()

    return instance


def update_instance(*, db_session, instance: WorkflowInstance, instance_in: WorkflowInstanceUpdate):
    """Updates an existing workflow instance."""
    instance_data = instance.dict()
    update_data = instance_in.dict(
        skip_defaults=True, exclude={"incident", "workflow", "creator", "artifacts"}
    )

    for a in instance_in.artifacts:
        artifact_document = document_service.get_or_create(db_session=db_session, document_in=a)
        instance.artifacts.append(artifact_document)

    for field in instance_data:
        if field in update_data:
            setattr(instance, field, update_data[field])

    db_session.commit()
    return instance


def run(
    *, db_session, workflow: Workflow, workflow_instance_in: WorkflowInstanceCreate
) -> WorkflowInstance:
    """Runs a workflow with the given parameters."""
    instance = create_instance(
        db_session=db_session,
        workflow=workflow,
        instance_in=WorkflowInstanceCreate(**workflow_instance_in.dict()),
    )

    # workflow plugins assume dictionary for params and do not accept none types
    params = {}
    for p in instance.parameters:
        if p["value"]:
            params.update({p["key"]: p["value"]})

    if instance.incident:
        params.update(
            {
                "externalRef": f"{DISPATCH_UI_URL}/{instance.incident.project.organization.name}/incidents/{instance.incident.name}?project={instance.incident.project.name}",
            }
        )

    if instance.case:
        params.update(
            {
                "externalRef": f"{DISPATCH_UI_URL}/{instance.case.project.organization.name}/cases/{instance.case.name}?project={instance.case.project.name}",
            }
        )

    params.update({"workflowInstanceId": instance.id})
    instance.workflow.plugin_instance.instance.run(instance.workflow.resource_id, params)

    return instance
