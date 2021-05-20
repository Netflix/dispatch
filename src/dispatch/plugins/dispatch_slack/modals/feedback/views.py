import json
from enum import Enum

from dispatch.incident.models import Incident
from dispatch.feedback.enums import FeedbackRating


class RatingFeedbackBlockId(str, Enum):
    anonymous = "anonymous_field"
    feedback = "feedback_field"
    rating = "rating_field"


class RatingFeedbackCallbackId(str, Enum):
    submit_form = "rating_feedback_submit_form"


def rating_feedback_view(incident: Incident):
    """Builds all blocks required to rate and provide feedback about an incident."""
    modal_template = {
        "type": "modal",
        "title": {"type": "plain_text", "text": "Incident Feedback"},
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Use this form to rate your experience and provide feedback about the incident.",
                    }
                ],
            },
        ],
        "close": {"type": "plain_text", "text": "Cancel"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "callback_id": RatingFeedbackCallbackId.submit_form,
        "private_metadata": json.dumps(
            {"incident_id": str(incident.id), "channel_id": incident.conversation.channel_id}
        ),
    }

    rating_picker_options = []
    for rating in FeedbackRating:
        rating_picker_options.append(
            {"text": {"type": "plain_text", "text": rating.value}, "value": rating.value}
        )

    rating_picker_block = {
        "type": "input",
        "block_id": RatingFeedbackBlockId.rating,
        "label": {"type": "plain_text", "text": "Rate your experience"},
        "element": {
            "type": "static_select",
            "placeholder": {"type": "plain_text", "text": "Select a rating"},
            "options": rating_picker_options,
        },
        "optional": False,
    }
    modal_template["blocks"].append(rating_picker_block)

    feedback_block = {
        "type": "input",
        "block_id": RatingFeedbackBlockId.feedback,
        "label": {"type": "plain_text", "text": "Give us feedback"},
        "element": {
            "type": "plain_text_input",
            "action_id": RatingFeedbackBlockId.feedback,
            "placeholder": {
                "type": "plain_text",
                "text": "How would you describe your experience?",
            },
            "multiline": True,
        },
        "optional": True,
    }
    modal_template["blocks"].append(feedback_block)

    anonymous_checkbox_block = {
        "type": "input",
        "block_id": RatingFeedbackBlockId.anonymous,
        "label": {
            "type": "plain_text",
            "text": "Check the box if you wish to provide your feedback anonymously",
        },
        "element": {
            "type": "checkboxes",
            "action_id": RatingFeedbackBlockId.anonymous,
            "options": [
                {
                    "value": "anonymous",
                    "text": {"type": "plain_text", "text": "Anonymize my feedback"},
                },
            ],
        },
        "optional": True,
    }
    modal_template["blocks"].append(anonymous_checkbox_block)

    return modal_template
