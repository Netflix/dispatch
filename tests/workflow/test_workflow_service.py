from tests.conftest import plugin_instance


def test_get(session, workflow):
    from dispatch.workflow.service import get

    t_workflow = get(db_session=session, workflow_id=workflow.id)
    assert t_workflow.id == workflow.id


def test_get_instance(session, workflow_instance):
    from dispatch.workflow.service import get_instance

    t_workflow_instance = get_instance(db_session=session, instance_id=workflow_instance.id)
    assert t_workflow_instance.id == workflow_instance.id


def test_create(session, project, plugin_instance):
    from dispatch.workflow.service import create
    from dispatch.workflow.models import WorkflowCreate

    name = "name"
    description = "description"
    resource_id = "resource_id"
    parameters = [{}]
    enabled = True

    workflow_in = WorkflowCreate(
        name=name,
        description=description,
        resource_id=resource_id,
        parameters=parameters,
        enabled=enabled,
        plugin_instance=plugin_instance,
        project=project,
    )
    workflow = create(db_session=session, workflow_in=workflow_in)
    assert workflow


def test_create_instance(session, incident, workflow, participant, project):
    from dispatch.workflow.service import create_instance
    from dispatch.workflow.models import WorkflowInstanceCreate
    from dispatch.document.models import DocumentCreate

    parameters = [{}]
    run_reason = "reason"
    status = "Submitted"

    artifacts = [
        DocumentCreate(
            name="name",
            resource_id="resource_id",
            resource_type="resource_type",
            project=project,
            weblink="https://www.example.com/doc",
        )
    ]

    instance_in = WorkflowInstanceCreate(
        parameters=parameters,
        run_reason=run_reason,
        status=status,
        incident=incident,
        workflow=workflow,
        creator=participant,
        artifacts=artifacts,
    )
    workflow_instance = create_instance(db_session=session, instance_in=instance_in)
    assert workflow_instance


def test_update(session, workflow):
    from dispatch.workflow.service import update
    from dispatch.workflow.models import WorkflowUpdate

    name = "Updated name"
    resource_id = "resource_id_updated"

    workflow_in = WorkflowUpdate(
        name=name,
        plugin_instance=workflow.plugin_instance,
        resource_id=resource_id,
    )
    workflow = update(
        db_session=session,
        workflow=workflow,
        workflow_in=workflow_in,
    )
    assert workflow.name == name
    assert workflow.resource_id == resource_id


def test_update_instance(session, workflow_instance):
    from dispatch.workflow.service import update_instance
    from dispatch.workflow.models import WorkflowInstanceUpdate

    status = "Running"

    workflow_instance_in = WorkflowInstanceUpdate(
        status=status,
    )
    workflow_instance = update_instance(
        db_session=session,
        instance=workflow_instance,
        instance_in=workflow_instance_in,
    )
    assert workflow_instance.status == status


def test_delete(session, workflow):
    from dispatch.workflow.service import delete, get

    delete(db_session=session, workflow_id=workflow.id)
    assert not get(db_session=session, workflow_id=workflow.id)
