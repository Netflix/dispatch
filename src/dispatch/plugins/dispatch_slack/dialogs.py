import logging

from dispatch.incident import service as incident_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.plugins.dispatch_slack.decorators import slack_background_task
from dispatch.report import service as report_service
from dispatch.report.enums import ReportTypes
from dispatch.service import service as service_service

from .config import SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG


log = logging.getLogger(__name__)


@slack_background_task
def create_assign_role_dialog(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Creates a dialog for assigning a role."""
    role_options = []
    for role in ParticipantRoleType:
        if role != ParticipantRoleType.participant:
            role_options.append({"label": role.value, "value": role.value})

    dialog = {
        "callback_id": command["command"],
        "title": "Assign Role",
        "submit_label": "Assign",
        "elements": [
            {
                "label": "Participant",
                "type": "select",
                "name": "participant",
                "data_source": "users",
            },
            {"label": "Role", "type": "select", "name": "role", "options": role_options},
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@slack_background_task
def create_engage_oncall_dialog(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Creates a dialog to engage an oncall person."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    oncall_services = service_service.get_all_by_project_id_and_status(
        db_session=db_session, project_id=incident.project.id, is_active=True
    )

    if not oncall_services.count():
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "No oncall services have been defined. You can define them in the Dispatch UI at /services",
                },
            }
        ]
        dispatch_slack_service.send_ephemeral_message(
            slack_client,
            channel_id,
            user_id,
            "No oncall services defined",
            blocks=blocks,
        )
        return

    oncall_service_options = []
    for oncall_service in oncall_services:
        oncall_service_options.append(
            {"label": oncall_service.name, "value": oncall_service.external_id}
        )

    page_options = [{"label": "Yes", "value": "Yes"}, {"label": "No", "value": "No"}]

    dialog = {
        "callback_id": command["command"],
        "title": "Engage Oncall",
        "submit_label": "Engage",
        "elements": [
            {
                "label": "Oncall Service",
                "type": "select",
                "name": "oncall_service_external_id",
                "options": oncall_service_options,
            },
            {
                "label": "Page",
                "type": "select",
                "name": "page",
                "value": "No",
                "options": page_options,
            },
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@slack_background_task
def create_tactical_report_dialog(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Creates a dialog with the most recent tactical report data, if it exists."""
    # we load the most recent tactical report
    tactical_report = report_service.get_most_recent_by_incident_id_and_type(
        db_session=db_session, incident_id=incident_id, report_type=ReportTypes.tactical_report
    )

    conditions = actions = needs = ""
    if tactical_report:
        conditions = tactical_report.details.get("conditions")
        actions = tactical_report.details.get("actions")
        needs = tactical_report.details.get("needs")

    dialog = {
        "callback_id": command["command"],
        "title": "Tactical Report",
        "submit_label": "Submit",
        "elements": [
            {"type": "textarea", "label": "Conditions", "name": "conditions", "value": conditions},
            {"type": "textarea", "label": "Actions", "name": "actions", "value": actions},
            {"type": "textarea", "label": "Needs", "name": "needs", "value": needs},
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@slack_background_task
def create_executive_report_dialog(
    user_id: str,
    user_email: str,
    channel_id: str,
    incident_id: int,
    command: dict = None,
    db_session=None,
    slack_client=None,
):
    """Creates a dialog with the most recent executive report data, if it exists."""
    # we load the most recent executive report
    executive_report = report_service.get_most_recent_by_incident_id_and_type(
        db_session=db_session, incident_id=incident_id, report_type=ReportTypes.executive_report
    )

    current_status = overview = next_steps = ""
    if executive_report:
        current_status = executive_report.details.get("current_status")
        overview = executive_report.details.get("overview")
        next_steps = executive_report.details.get("next_steps")

    dialog = {
        "callback_id": command["command"],
        "title": "Executive Report",
        "submit_label": "Submit",
        "elements": [
            {
                "type": "textarea",
                "label": "Current Status",
                "name": "current_status",
                "value": current_status,
            },
            {"type": "textarea", "label": "Overview", "name": "overview", "value": overview},
            {
                "type": "textarea",
                "label": "Next Steps",
                "name": "next_steps",
                "value": next_steps,
                "hint": f"Use {SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG} to update the list of recipients of this report.",
            },
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)
