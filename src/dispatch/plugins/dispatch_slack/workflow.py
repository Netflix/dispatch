from blockkit import Context, Input, Section, MarkdownText, Modal, PlainTextInput, Message

from dispatch.config import DISPATCH_UI_URL
from dispatch.database.core import SessionLocal
from dispatch.enums import DispatchEnum
from dispatch.incident import service as incident_service
from dispatch.messaging.strings import INCIDENT_WORKFLOW_CREATED_NOTIFICATION
from dispatch.participant import service as participant_service
from dispatch.plugins.dispatch_slack.bolt import app
from dispatch.plugins.dispatch_slack.middleware import (
    action_context_middleware,
    command_context_middleware,
    modal_submit_middleware,
    db_middleware,
    user_middleware,
)
from dispatch.plugins.dispatch_slack.fields import static_select_block
from dispatch.workflow import service as workflow_service
from dispatch.workflow.flows import send_workflow_notification
from dispatch.workflow.models import WorkflowInstanceCreate


class RunWorkflowBlockIds(DispatchEnum):
    workflow_select = "run-workflow-select"
    reason_input = "run-workflow-reason-input"
    param_input = "run-workflow-param-input"


class RunWorkflowActionIds(DispatchEnum):
    workflow_select = "run-workflow-workflow-select"
    reason_input = "run-workflow-reason-input"
    param_input = "run-workflow-param-input"


class RunWorkflowActions(DispatchEnum):
    submit = "run-workflow-submit"
    workflow_select = "run-workflow-workflow-select"


def configure(config):
    """Maps commands/events to their functions."""
    middleware = [command_context_middleware, db_middleware]
    app.command(config.slack_command_list_workflows, middleware=middleware)(
        handle_workflow_list_command
    )
    app.command(config.slack_command_run_workflow, middleware=middleware)(
        handle_workflow_run_command
    )


def workflow_select(
    db_session: SessionLocal,
    project_id: int,
    action_id: str = RunWorkflowActionIds.workflow_select,
    block_id: str = RunWorkflowBlockIds.workflow_select,
    initial_option: dict = None,
    label: str = "Workflow",
    **kwargs,
):
    workflows = workflow_service.get_enabled(db_session=db_session, project_id=project_id)

    return static_select_block(
        action_id=action_id,
        block_id=block_id,
        initial_option=initial_option,
        label=label,
        options=[{"text": w.name, "value": w.id} for w in workflows],
        placeholder="Select Workflow",
        **kwargs,
    )


def reason_input(
    action_id: str = RunWorkflowActionIds.reason_input,
    block_id: str = RunWorkflowBlockIds.reason_input,
    initial_value: str = None,
    label: str = "Reason",
    **kwargs,
):
    return Input(
        block_id=block_id,
        element=PlainTextInput(
            action_id=action_id,
            initial_value=initial_value,
            multiline=True,
            placeholder="Short description why workflow was run.",
        ),
        label=label,
        **kwargs,
    )


def param_input(
    action_id: str = RunWorkflowActionIds.param_input,
    block_id: str = RunWorkflowBlockIds.param_input,
    initial_options: list = None,
    label: str = "Workflow Parameters",
    **kwargs,
):
    inputs = []
    for p in initial_options:
        inputs.append(
            Input(
                block_id=f"{block_id}-{p['key']}",
                element=PlainTextInput(
                    placeholder="Parameter Value",
                    action_id=f"{action_id}-{p['key']}",
                    initial_value=p["value"],
                ),
                label=p["key"],
                **kwargs,
            )
        )
    return inputs


async def handle_workflow_list_command(ack, body, respond, client, context, db_session):
    """Handles the workflow list command."""
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
    workflows = incident.workflow_instances

    blocks = [Section(text="*Workflows*")]
    for w in workflows:
        artifact_links = ""
        for a in w.artifacts:
            artifact_links += f"- <{a.weblink}|{a.name}> \n"

        blocks.append(
            Section(
                fields=[
                    f"*Name:* \n <{w.weblink}|{w.workflow.name}>"
                    f"*Workflow Description:* \n {w.workflow.description}"
                    f"*Run Reason:* \n {w.run_reason}"
                    f"*Creator:* \n {w.creator.individual.name}"
                    f"*Status:* \n {w.status}"
                    f"*Artifacts:* \n {artifact_links}"
                ]
            )
        )

    blocks = Message(blocks=blocks).build()["blocks"]
    await respond(blocks=blocks, response_type="ephemeral")


async def handle_workflow_run_command(
    ack,
    body,
    client,
    context,
    db_session,
):
    """Handles the workflow run command."""
    await ack()
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    blocks = [
        Context(elements=[MarkdownText(text="Select a workflow to run.")]),
        workflow_select(
            db_session=db_session, dispatch_action=True, project_id=incident.project.id
        ),
    ]

    modal = Modal(
        title="Run Workflow",
        blocks=blocks,
        submit="Run",
        close="Close",
        callback_id=RunWorkflowActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_open(view=modal, trigger_id=body["trigger_id"])


@app.view(
    RunWorkflowActions.submit,
    middleware=[action_context_middleware, db_middleware, user_middleware, modal_submit_middleware],
)
async def handle_workflow_submission_event(ack, body, client, context, db_session, form_data, user):
    """Handles workflow submission event."""
    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)

    workflow_id = form_data.get(RunWorkflowBlockIds.workflow_select)["value"]
    workflow = workflow_service.get(db_session=db_session, workflow_id=workflow_id)

    params = {}
    named_params = []
    for i in form_data.keys():
        if i.startswith(RunWorkflowBlockIds.param_input):
            key = i.split("-")[1]
            value = form_data[i]
            params.update({key: value})
            named_params.append({"key": key, "value": value})

    creator = participant_service.get_by_incident_id_and_email(
        db_session=db_session, incident_id=incident.id, email=user.email
    )

    instance = workflow_service.create_instance(
        db_session=db_session,
        instance_in=WorkflowInstanceCreate(
            workflow=workflow,
            incident=incident,
            creator=creator,
            run_reason=form_data[RunWorkflowBlockIds.reason_input],
            parameters=named_params,
        ),
    )

    for p in instance.parameters:
        if p["value"]:
            params.update({p["key"]: p["value"]})

    params.update(
        {
            "externalRef": f"{DISPATCH_UI_URL}/{instance.incident.project.organization.name}/incidents/{instance.incident.name}?project={instance.incident.project.name}",
            "workflowInstanceId": instance.id,
        }
    )

    workflow.plugin_instance.instance.run(workflow.resource_id, params)

    # TODO we should move off these types of notification functions and create them directly
    send_workflow_notification(
        incident.project.id,
        incident.conversation.channel_id,
        INCIDENT_WORKFLOW_CREATED_NOTIFICATION,
        db_session,
        instance_creator_name=instance.creator.individual.name,
        workflow_name=instance.workflow.name,
        workflow_description=instance.workflow.description,
    )


@app.action(
    RunWorkflowActions.workflow_select, middleware=[action_context_middleware, db_middleware]
)
async def handle_run_workflow_select_action(ack, body, db_session, context, client):
    """Handles workflow select event."""
    await ack()
    values = body["view"]["state"]["values"]
    workflow_id = values[RunWorkflowBlockIds.workflow_select][RunWorkflowActionIds.workflow_select][
        "selected_option"
    ]["value"]

    incident = incident_service.get(db_session=db_session, incident_id=context["subject"].id)
    selected_workflow = workflow_service.get(db_session=db_session, workflow_id=workflow_id)

    blocks = [
        Context(elements=[MarkdownText(text="Select a workflow to run.")]),
        workflow_select(
            initial_option={"text": selected_workflow.name, "value": selected_workflow.id},
            db_session=db_session,
            dispatch_action=True,
            project_id=incident.project.id,
        ),
        reason_input(),
    ]

    blocks.extend(
        param_input(initial_options=selected_workflow.parameters),
    )

    modal = Modal(
        title="Run Workflow",
        blocks=blocks,
        submit="Run",
        close="Close",
        callback_id=RunWorkflowActions.submit,
        private_metadata=context["subject"].json(),
    ).build()

    await client.views_update(
        view_id=body["view"]["id"],
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=modal,
    )
