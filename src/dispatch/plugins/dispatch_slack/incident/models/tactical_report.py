from pydantic import BaseModel, model_validator
from typing import Literal

"""
{
        "type": "input",
        "block_id": "report-tactical-conditions",
        "label": {
          "type": "plain_text",
          "text": "Conditions",
          "emoji": true
        },
        "optional": false,
        "dispatch_action": false,
        "element": {
          "type": "plain_text_input",
          "placeholder": {
            "type": "plain_text",
            "text": "Current incident conditions",
            "emoji": true
          },
          "initial_value": "conditions",
          "multiline": true,
          "dispatch_action_config": {
            "trigger_actions_on": [
              "on_enter_pressed"
            ]
          },
          "action_id": "URBqW"
        }
        """

class Block(BaseModel):
    type: str
    block_id: str


class ConditionsBlock(BaseModel):
    block_id: Literal["report-tactical-conditions"]

class ActionsBlock(BaseModel):
    block_id: Literal["report-tactical-actions"]

class NeedsBlock(BaseModel):
    block_id: Literal["report-tactical-needs"]

class DraftOrLoadingBlock(BaseModel):
    """
    Block model for either the "draft with genai" option button or loading.
    """


class TacticalReportBlocks(BaseModel):
    """
    The four blocks comprising a tactical report.
    """
    conditions_block: ConditionsBlock




class TacticalReportView(BaseModel):
    """
    Modal view for tactical reports. This view is updated in-place and has multiple components,
    so we store them here to enforce structural consistency.
    """
    id: str
    team_id: str
    type: Literal["modal"]
    blocks: TacticalReportBlocks
"""

 "view": {
    "id": "V096X3H667K",
    "team_id": "T085M7R5S5A",
    "type": "modal",
    "blocks": [
      {
        "type": "input",
        "block_id": "report-tactical-conditions",
        "label": {
          "type": "plain_text",
          "text": "Conditions",
          "emoji": true
        },
        "optional": false,
        "dispatch_action": false,
        "element": {
          "type": "plain_text_input",
          "placeholder": {
            "type": "plain_text",
            "text": "Current incident conditions",
            "emoji": true
          },
          "initial_value": "conditions",
          "multiline": true,
          "dispatch_action_config": {
            "trigger_actions_on": [
              "on_enter_pressed"
            ]
          },
          "action_id": "URBqW"
        }
      },
      {
        "type": "input",
        "block_id": "report-tactical-actions",
        "label": {
          "type": "plain_text",
          "text": "Actions",
          "emoji": true
        },
        "optional": false,
        "dispatch_action": false,
        "element": {
          "type": "plain_text_input",
          "placeholder": {
            "type": "plain_text",
            "text": "Current incident actions",
            "emoji": true
          },
          "initial_value": "actions",
          "multiline": true,
          "dispatch_action_config": {
            "trigger_actions_on": [
              "on_enter_pressed"
            ]
          },
          "action_id": "AVSMK"
        }
      },
      {
        "type": "input",
        "block_id": "report-tactical-needs",
        "label": {
          "type": "plain_text",
          "text": "Needs",
          "emoji": true
        },
        "optional": false,
        "dispatch_action": false,
        "element": {
          "type": "plain_text_input",
          "placeholder": {
            "type": "plain_text",
            "text": "Current incident needs",
            "emoji": true
          },
          "initial_value": "needs. submission test",
          "multiline": true,
          "dispatch_action_config": {
            "trigger_actions_on": [
              "on_enter_pressed"
            ]
          },
          "action_id": "5bmCj"
        }
      },
      {
        "type": "actions",
        "block_id": "W6vtl",
        "elements": [
          {
            "type": "button",
            "action_id": "tactical_report_genai",
            "text": {
              "type": "plain_text",
              "text": ":sparkles: Draft with GenAI",
              "emoji": true
            },
            "style": "primary",
            "value": "{\"id\":\"687\",\"type\":\"incident\",\"organization_slug\":\"default\",\"project_id\":\"1\",\"channel_id\":null,\"thread_id\":null}"
          }
        ]
      }
    ],
    "private_metadata": "{\"id\":\"687\",\"type\":\"incident\",\"organization_slug\":\"default\",\"project_id\":\"1\",\"channel_id\":null,\"thread_id\":null}",
    "callback_id": "report-tactical-submit",
    "state": {
      "values": {
        "report-tactical-conditions": {
          "URBqW": {
            "type": "plain_text_input",
            "value": "conditions"
          }
        },
        "report-tactical-actions": {
          "AVSMK": {
            "type": "plain_text_input",
            "value": "actions"
          }
        },
        "report-tactical-needs": {
          "5bmCj": {
"""
