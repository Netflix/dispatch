from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from dispatch.plugin import service as plugin_service

from .models import Workflow, WorkflowCreate, WorkflowUpdate


def get(*, db_session, workflow_id: int) -> Optional[Workflow]:
    """Returns a workflow based on the given workflow id."""
    return db_session.query(Workflow).filter(Workflow.id == workflow_id).one_or_none()


def get_all(*, db_session) -> List[Optional[Workflow]]:
    """Returns all workflows."""
    return db_session.query(Workflow)


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
