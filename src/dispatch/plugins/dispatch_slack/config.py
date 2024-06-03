from typing import Optional
from pydantic import Field, SecretStr
from dispatch.config import BaseConfigurationModel


class SlackConfiguration(BaseConfigurationModel):
    """Slack configuration description."""

    api_bot_token: SecretStr = Field(
        title="API Bot Token", description="Token to use when plugin is in http/api mode."
    )
    socket_mode_app_token: Optional[SecretStr] = Field(
        title="Socket Mode App Token", description="Token used when plugin is in socket mode."
    )
    signing_secret: SecretStr = Field(
        title="Signing Secret",
        description="Secret used to validate incoming messages from the Slack events API.",
    )


class SlackContactConfiguration(SlackConfiguration):
    """Slack contact configuration."""

    profile_department_field_id: Optional[str] = Field(
        None,
        title="Profile Department Field Id",
        description="Defines the field in the slack profile where Dispatch should fetch the users department.",
    )
    profile_team_field_id: Optional[str] = Field(
        title="Profile Team Field Id",
        description="Defines the field in the slack profile where Dispatch should fetch a users team.",
    )
    profile_weblink_field_id: Optional[str] = Field(
        title="Profile Weblink Field Id",
        description="Defines the field in the slack profile where Dispatch should fetch the users weblink.",
    )


class SlackConversationConfiguration(SlackConfiguration):
    """Slack conversation configuration."""

    app_user_slug: str = Field(
        title="App User Id",
        description="Defines the user id of the Slack app in your environment. You can use Slack's tester endpoint auth.test to find the user id.",
    )
    private_channels: bool = Field(
        True,
        title="Private Channels",
        description="The visibility of the slack channel created by Dispatch.",
    )
    ban_threads: bool = Field(
        True,
        title="Ban Threads",
        description="If enabled, Dispatch will message users reminding them to not use threads in incident channels.",
    )
    timeline_event_reaction: str = Field(
        "stopwatch",
        title="Timeline Event Reaction",
        description="Defines the emoji that Dispatch will monitor for adding slack messages to the timeline.",
    )
    slack_command_list_tasks: str = Field(
        "/dispatch-list-tasks",
        title="List Tasks Command String",
        description="Defines the string used to list all tasks in an incident. Must match what is defined in Slack.",
    )
    slack_command_list_my_tasks: str = Field(
        "/dispatch-list-my-tasks",
        title="List My Tasks Command String",
        description="Defines the string used to list a caller's tasks in an incident. Must match what is defined in Slack.",
    )
    slack_command_list_participants: str = Field(
        "/dispatch-list-participants",
        title="List Participants Command String",
        description="Defines the string used to list all incident participants. Must match what is defined in Slack.",
    )
    slack_command_list_signals: str = Field(
        "/dispatch-list-signals",
        title="List Signals Command String",
        description="Defines the string used to list all signals for the conversation where the command was ran. Must match what is defined in Slack.",
    )
    slack_command_assign_role: str = Field(
        "/dispatch-assign-role",
        title="Assign Role Command String",
        description="Defines the string used to assign a role in an incident. Must match what is defined in Slack.",
    )
    slack_command_update_incident: str = Field(
        "/dispatch-update-incident",
        title="Update Incident Command String",
        description="Defines the string used to update an incident. Must match what is defined in Slack.",
    )
    slack_command_update_participant: str = Field(
        "/dispatch-update-participant",
        title="Update Participant Command String",
        description="Defines the string used to update a participant. Must match what is defined in Slack.",
    )
    slack_command_engage_oncall: str = Field(
        "/dispatch-engage-oncall",
        title="Engage Oncall Command String",
        description="Defines the string used to engage an oncall. Must match what is defined in Slack.",
    )
    slack_command_update_case: str = Field(
        "/dispatch-update-case",
        title="Update Case Command String",
        description="Defines the string used to update a case. Must match what is defined in Slack.",
    )
    slack_command_escalate_case: str = Field(
        "/dispatch-escalate-case",
        title="Escalates a case to an incident",
        description="Only works from within a channel based Case.",
    )
    slack_command_report_incident: str = Field(
        "/dispatch-report-incident",
        title="Report Incident Command String",
        description="Defines the string used to report an incident. Must match what is defined in Slack.",
    )
    slack_command_report_tactical: str = Field(
        "/dispatch-report-tactical",
        title="Report Tactical Command String",
        description="Defines the string used to create a tactical report. Must match is defined in Slack.",
    )
    slack_command_report_executive: str = Field(
        "/dispatch-report-executive",
        title="Report Executive Command String",
        description="Defines the string used to create an executive report. Must match what is defined in Slack.",
    )
    slack_command_update_notifications_group: str = Field(
        "/dispatch-notifications-group",
        title="Update Notifications Group Command String",
        description="Defines the string used to update the incident notification group. Must match what is defined in Slack.",
    )
    slack_command_add_timeline_event: str = Field(
        "/dispatch-add-timeline-event",
        title="Add Timeline Event Command String",
        description="Defines the string used to add a new event to the timeline. Must match what is defined in Slack",
    )
    slack_command_list_incidents: str = Field(
        "/dispatch-list-incidents",
        title="List Incidents Command String",
        description="Defines the string used to list current active and stable incidents, and closed incidents in the last 24 hours. Must match what is defined in Slack.",
    )
    slack_command_run_workflow: str = Field(
        "/dispatch-run-workflow",
        title="Run Workflow Command String",
        description="Defines the string used to run a workflow. Must match what is defined in Slack.",
    )
    slack_command_list_workflows: str = Field(
        "/dispatch-list-workflows",
        title="List Workflows Command String",
        description="Defines the string used to list all available workflows. Must match what is defined in Slack",
    )
