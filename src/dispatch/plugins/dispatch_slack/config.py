from pydantic.main import BaseModel, Field, SecretStr


class SlackConfiguration(BaseModel):
    """Slack configuration description."""

    api_bot_token: SecretStr = Field(None, title="API Bot Token", description="")
    socket_mode_app_token: SecretStr = Field(None, title="Socket Mode App Token", description="")
    app_user_slug: str = Field(None, title="App User Slug")
    ban_threads: bool = Field(True, title="Ban Threads", description="")
    profile_department_field_id: str = Field(
        None, title="Profile Department Field Id", description=""
    )
    profile_team_field_id: str = Field(None, title="Profile Team Field Id", description="")
    signing_secret: SecretStr = Field(None, title="Signing Secret", description="")
    timeline_event_reaction: str = Field(
        "stopwatch", title="Timeline Event Reaction", description=""
    )
    user_id_override: str = Field(None, title="User Id Override", description="")
    slash_command_list_tasks: str = Field(
        "/dispatch-list-tasks",
        title="List Tasks Command String",
        description="Defines the string used to list all incidents in an incident. Must match what is defined in Slack.",
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
    slack_command_assign_role: str = Field(
        "/dispatch-assign-role",
        title="Assign Role Command String",
        description="Defines the string used assign a role in an incident. Must match what is defined in Slack.",
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
    slack_command_list_resources: str = Field(
        "/dispatch-list-resources",
        title="List Resources Command String",
        description="Defines the string used to list incident resources. Must match what is defined in Slack.",
    )
    slack_command_report_incident: str = Field(
        "/dispatch-report-incident",
        title="Report Incident Command String",
        description="Defines the string used to report an incident. Must match what is defined in Slack.",
    )
    slack_command_report_tactical: str = Field(
        "/dispatch-report-tactical",
        title="Report Tactical Command String",
        description="Defines the string used to create an tactical report. Must match is defined in Slack.",
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
        description="Defines the string used to list all current incidents. Must match what is defined in Slack.",
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
