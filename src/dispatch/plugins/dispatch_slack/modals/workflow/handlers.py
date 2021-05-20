from dispatch.messaging.strings import INCIDENT_WORKFLOW_CREATED_NOTIFICATION
from dispatch.incident import service as incident_service
from dispatch.workflow import service as workflow_service
from dispatch.workflow.models import WorkflowInstanceCreate
from dispatch.workflow.flows import send_workflow_notification

from dispatch.plugins.dispatch_slack.modals.common import parse_submitted_form
from dispatch.plugins.dispatch_slack.decorators import slack_background_task
from dispatch.plugins.dispatch_slack.service import (
    send_ephemeral_message,
    open_modal_with_user,
    update_modal_with_user,
    get_user_email,
)

from .views import run_workflow_view, RunWorkflowBlockId, RunWorkflowCallbackId


@slack_background_task
def create_run_workflow_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict,
    db_session=None,
    slack_client=None,
):
    """Creates a modal for running a workflow."""
    trigger_id = command.get("trigger_id")

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    workflows = workflow_service.get_enabled(db_session=db_session)

    if workflows:
        modal_create_template = run_workflow_view(incident=incident, workflows=workflows)

        open_modal_with_user(
            client=slack_client, trigger_id=trigger_id, modal=modal_create_template
        )
    else:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "No workflows are enabled. You can enable one in the Dispatch UI at /workflows.",
                },
            }
        ]
        send_ephemeral_message(
            slack_client,
            command["channel_id"],
            command["user_id"],
            "No workflows enabled.",
            blocks=blocks,
        )


@slack_background_task
def update_workflow_modal(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Pushes an updated view to the run workflow modal."""
    trigger_id = action["trigger_id"]
    incident_id = action["view"]["private_metadata"]["incident_id"]
    workflow_id = action["actions"][0]["selected_option"]["value"]

    selected_workflow = workflow_service.get(db_session=db_session, workflow_id=workflow_id)
    workflows = workflow_service.get_enabled(db_session=db_session)
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    modal_template = run_workflow_view(
        incident=incident, workflows=workflows, selected_workflow=selected_workflow
    )

    modal_template["blocks"].append(
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Description* \n {selected_workflow.description}"},
        },
    )

    modal_template["blocks"].append(
        {
            "block_id": RunWorkflowBlockId.run_reason,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": RunWorkflowBlockId.run_reason,
            },
            "label": {"type": "plain_text", "text": "Run Reason"},
        },
    )

    modal_template["blocks"].append(
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Parameters*"}}
    )

    if selected_workflow.parameters:
        for p in selected_workflow.parameters:
            modal_template["blocks"].append(
                {
                    "block_id": f"{RunWorkflowBlockId.param}-{p['key']}",
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "placeholder": {"type": "plain_text", "text": "Value"},
                    },
                    "label": {"type": "plain_text", "text": p["key"]},
                }
            )

    else:
        modal_template["blocks"].append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "This workflow has no parameters."},
            }
        )

    modal_template["callback_id"] = RunWorkflowCallbackId.submit_form

    update_modal_with_user(
        client=slack_client,
        trigger_id=trigger_id,
        view_id=action["view"]["id"],
        modal=modal_template,
    )


@slack_background_task
def run_workflow_submitted_form(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    action: dict,
    db_session=None,
    slack_client=None,
):
    """Runs an external flow."""
    submitted_form = action.get("view")
    parsed_form_data = parse_submitted_form(submitted_form)

    params = {}
    named_params = []
    for i in parsed_form_data.keys():
        if i.startswith(RunWorkflowBlockId.param):
            key = i.split("-")[1]
            value = parsed_form_data[i]
            params.update({key: value})
            named_params.append({"key": key, "value": value})

    workflow_id = parsed_form_data.get(RunWorkflowBlockId.workflow_select)["value"]
    run_reason = parsed_form_data.get(RunWorkflowBlockId.run_reason)
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)
    workflow = workflow_service.get(db_session=db_session, workflow_id=workflow_id)

    creator_email = get_user_email(slack_client, action["user"]["id"])

    instance = workflow_service.create_instance(
        db_session=db_session,
        instance_in=WorkflowInstanceCreate(
            workflow={"id": workflow.id},
            incident={"id": incident.id},
            creator={"email": creator_email},
            run_reason=run_reason,
            parameters=named_params,
        ),
    )
    params.update(
        {"incident_id": incident.id, "incident_name": incident.name, "instance_id": instance.id}
    )

    workflow.plugin.instance.run(workflow.resource_id, params)

    send_workflow_notification(
        incident.conversation.channel_id,
        INCIDENT_WORKFLOW_CREATED_NOTIFICATION,
        db_session,
        instance_creator_name=instance.creator.individual.name,
        workflow_name=instance.workflow.name,
        workflow_description=instance.workflow.description,
    )
