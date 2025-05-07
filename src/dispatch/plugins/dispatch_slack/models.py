"""Models for Slack command payloads in the Dispatch application."""

from typing import NewType, TypedDict

from pydantic import BaseModel, AnyHttpUrl

from dispatch.enums import DispatchEnum


class SlackCommandPayload(TypedDict):
    """TypedDict for Slack command payload values."""

    token: str
    team_id: str
    team_domain: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    command: str
    text: str
    api_app_id: str
    is_enterprise_install: str
    response_url: str
    trigger_id: str


class SubjectMetadata(BaseModel):
    """Base model for subject metadata in Slack payloads."""

    id: str | None = None
    type: str | None = None
    organization_slug: str = "default"

    project_id: str | None = None
    channel_id: str | None = None
    thread_id: str | None = None


class AddUserMetadata(SubjectMetadata):
    """Model for metadata when adding users."""

    users: list[str]


class EngagementMetadata(SubjectMetadata):
    """Model for engagement-related metadata."""

    signal_instance_id: str
    engagement_id: int
    user: str | None = None


class TaskMetadata(SubjectMetadata):
    """Model for task-related metadata."""

    task_id: str | None = None
    resource_id: str | None = None
    action_type: str


class MonitorMetadata(SubjectMetadata):
    """Model for monitor-related metadata."""

    weblink: AnyHttpUrl | None = None
    plugin_instance_id: int


class BlockSelection(BaseModel):
    """Model for a block selection in Slack forms."""

    name: str
    value: str


FormData = NewType(
    "FormData",
    dict[
        str,
        str | BlockSelection | list[BlockSelection],
    ],
)


class FormMetadata(SubjectMetadata):
    """Model for form metadata in Slack payloads."""

    form_data: FormData


class CaseSubjects(DispatchEnum):
    """Enum for case subjects."""

    case = "case"


class IncidentSubjects(DispatchEnum):
    """Enum for incident subjects."""

    incident = "incident"


class SignalSubjects(DispatchEnum):
    """Enum for signal subjects."""

    signal = "signal"
    signal_instance = "signal_instance"
