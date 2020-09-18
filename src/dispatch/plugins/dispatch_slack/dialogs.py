import logging

from dispatch.decorators import background_task
from dispatch.enums import Visibility
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident_priority import service as incident_priority_service
from dispatch.incident_type import service as incident_type_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugins.dispatch_slack import service as dispatch_slack_service
from dispatch.report import service as report_service
from dispatch.report.enums import ReportTypes
from dispatch.service import service as service_service

from .config import SLACK_COMMAND_UPDATE_NOTIFICATIONS_GROUP_SLUG


slack_client = dispatch_slack_service.create_slack_client()
log = logging.getLogger(__name__)


def create_assign_role_dialog(incident_id: int, command: dict = None):
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


@background_task
def create_update_incident_dialog(incident_id: int, command: dict = None, db_session=None):
    """Creates a dialog for updating incident information."""
    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    type_options = []
    for t in incident_type_service.get_all(db_session=db_session):
        type_options.append({"label": t.name, "value": t.name})

    priority_options = []
    for priority in incident_priority_service.get_all(db_session=db_session):
        priority_options.append({"label": priority.name, "value": priority.name})

    status_options = []
    for status in IncidentStatus:
        status_options.append({"label": status.value, "value": status.value})

    visibility_options = []
    for visibility in Visibility:
        visibility_options.append({"label": visibility.value, "value": visibility.value})

    notify_options = [{"label": "Yes", "value": "Yes"}, {"label": "No", "value": "No"}]

    dialog = {
        "callback_id": command["command"],
        "title": "Update Incident",
        "submit_label": "Save",
        "elements": [
            {"type": "textarea", "label": "Title", "name": "title", "value": incident.title},
            {
                "type": "textarea",
                "label": "Description",
                "name": "description",
                "value": incident.description,
            },
            {
                "label": "Type",
                "type": "select",
                "name": "type",
                "value": incident.incident_type.name,
                "options": type_options,
            },
            {
                "label": "Priority",
                "type": "select",
                "name": "priority",
                "value": incident.incident_priority.name,
                "options": priority_options,
            },
            {
                "label": "Status",
                "type": "select",
                "name": "status",
                "value": incident.status,
                "options": status_options,
            },
            {
                "label": "Visibility",
                "type": "select",
                "name": "visibility",
                "value": incident.visibility,
                "options": visibility_options,
            },
            {
                "label": "Notify on change",
                "type": "select",
                "name": "notify",
                "value": "Yes",
                "options": notify_options,
            },
        ],
    }

    dispatch_slack_service.open_dialog_with_user(slack_client, command["trigger_id"], dialog)


@background_task
def create_engage_oncall_dialog(incident_id: int, command: dict = None, db_session=None):
    """Creates a dialog to engage an oncall person."""
    oncall_services = service_service.get_all_by_status(db_session=db_session, is_active=True)

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
            command["channel_id"],
            command["user_id"],
            "No Oncall Services Defined",
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
                "name": "oncall_service_id",
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


@background_task
def create_tactical_report_dialog(incident_id: int, command: dict = None, db_session=None):
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


@background_task
def create_executive_report_dialog(incident_id: int, command: dict = None, db_session=None):
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
