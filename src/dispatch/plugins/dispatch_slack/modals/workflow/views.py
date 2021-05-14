import json
from enum import Enum
from typing import List

from dispatch.incident.models import Incident
from dispatch.workflow.models import Workflow


class RunWorkflowBlockId(str, Enum):
    workflow_select = "run_workflow_select"
    run_reason = "run_workflow_run_reason"
    param = "run_workflow_param"


class RunWorkflowCallbackId(str, Enum):
    submit_form = "run_workflow_submit_form"
    update_view = "run_workflow_update_view"


def run_workflow_view(
    incident: Incident, workflows: List[Workflow], selected_workflow: Workflow = None
):
    """Builds all blocks required to run a workflow."""
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Run workflow"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Use this form to run a workflow.",
                    }
                ],
            },
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Run"},
        "callback_id": RunWorkflowCallbackId.update_view,
        "private_metadata": json.dumps(
            {"incident_id": str(incident.id), "channel_id": incident.conversation.channel_id}
        ),
    }

    selected_option = None
    workflow_options = []
    for w in workflows:
        # don't show disable workflows or workflows with disabled plugins
        if not w.plugin.enabled or not w.enabled:
            continue

        current_option = {
            "text": {
                "type": "plain_text",
                "text": w.name,
            },
            "value": str(w.id),
        }

        workflow_options.append(current_option)

        if selected_workflow:
            if w.id == selected_workflow.id:
                selected_option = current_option

    if selected_workflow:
        select_block = {
            "block_id": RunWorkflowBlockId.workflow_select,
            "type": "input",
            "element": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select Workflow",
                },
                "initial_option": selected_option,
                "options": workflow_options,
                "action_id": RunWorkflowBlockId.workflow_select,
            },
            "label": {"type": "plain_text", "text": "Workflow"},
        }
    else:
        select_block = {
            "block_id": RunWorkflowBlockId.workflow_select,
            "type": "actions",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select Workflow",
                    },
                    "options": workflow_options,
                }
            ],
        }

    modal_template["blocks"].append(select_block)

    return modal_template
