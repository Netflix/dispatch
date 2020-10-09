from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from sqlalchemy.sql.expression import true

from dispatch.plugin import service as plugin_service
from dispatch.incident import service as incident_service
from dispatch.participant import service as participant_service
from dispatch.document import service as document_service

from dispatch.document.models import DocumentCreate

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


def get_all(*, db_session) -> List[Optional[Workflow]]:
    """Returns all workflows."""
    return db_session.query(Workflow)


def get_enabled(*, db_session) -> List[Optional[Workflow]]:
    """Fetches all enabled workflows."""
    return db_session.query(Workflow).filter(Workflow.enabled == true()).all()


def create(*, db_session, workflow_in: WorkflowCreate) -> Workflow:
    """Creates a new workflow."""
    workflow = Workflow(
        **workflow_in.dict(exclude={"plugin"}),
    )
    plugin = plugin_service.get(db_session=db_session, plugin_id=workflow_in.plugin.id)
    workflow.plugin = plugin

    db_session.add(workflow)
    db_session.commit()
    return workflow


def update(*, db_session, workflow: Workflow, workflow_in: WorkflowUpdate) -> Workflow:
    """Updates a workflow."""
    workflow_data = jsonable_encoder(workflow)
    update_data = workflow_in.dict(skip_defaults=True, exclude={"plugin"})

    for field in workflow_data:
        if field in update_data:
            setattr(workflow, field, update_data[field])

    plugin = plugin_service.get(db_session=db_session, plugin_id=workflow_in.plugin.id)
    workflow.plugin = plugin

    db_session.add(workflow)
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


def create_instance(*, db_session, instance_in: WorkflowInstanceCreate) -> WorkflowInstance:
    """Creates a new workflow instance."""
    instance = WorkflowInstance(
        **instance_in.dict(exclude={"incident", "workflow", "creator", "artifacts"})
    )

    incident = incident_service.get(db_session=db_session, incident_id=instance_in.incident["id"])
    instance.incident = incident

    workflow = get(db_session=db_session, workflow_id=instance_in.workflow["id"])
    instance.workflow = workflow

    creator = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=instance_in.creator["email"]
    )
    instance.creator = creator

    for a in instance_in.artifacts:
        artifact_document = document_service.create(
            db_session=db_session, document_in=DocumentCreate(**a)
        )
        instance.artifacts.append(artifact_document)

    db_session.add(instance)
    db_session.commit()

    return instance


def update_instance(*, db_session, instance: WorkflowInstance, instance_in: WorkflowInstanceUpdate):
    """Updates an existing workflow instance."""
    instance_data = jsonable_encoder(instance)
    update_data = instance_in.dict(
        skip_defaults=True, exclude={"incident", "workflow", "creator", "artifacts"}
    )

    for a in instance_in.artifacts:
        artifact_document = document_service.get_or_create(db_session=db_session, document_in=a)
        instance.artifacts.append(artifact_document)

    for field in instance_data:
        if field in update_data:
            setattr(instance, field, update_data[field])

    db_session.add(instance)
    db_session.commit()

    return instance
