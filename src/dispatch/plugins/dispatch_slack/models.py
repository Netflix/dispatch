from typing import Optional, NewType, TypedDict

from pydantic import BaseModel, Field, AnyHttpUrl

from dispatch.enums import DispatchEnum


class SlackCommandPayload(TypedDict):
    """Example payload values:

    {
        "token": "fQLoLYUrEun9aDVHEHsPEH8N",
        "team_id": "T04FZTZLBFE",
        "team_domain": "netflix",
        "channel_id": "C06RQGTRSK0",
        "channel_name": "dispatch-default-test-5405",
        "user_id": "U04FUR31VCM",
        "user_name": "wshel",
        "command": "/dispatch-list-tasks",
        "text": "",
        "api_app_id": "A04FGTKNP2B",
        "is_enterprise_install": "false",
        "response_url": "https://hooks.slack.com/commands/T04FZTFLBFE/6904042509680/ZDe0xFBOrv88Rr6vUoioc6Tm",
        "trigger_id": "6866691537272.4543933691524.06904af71159927b69bfe32f47ddd5a5",
    }
    """

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
    id: Optional[str]
    type: Optional[str]
    organization_slug: str = "default"

    project_id: Optional[str]
    channel_id: Optional[str]


class EngagementMetadata(SubjectMetadata):
    signal_instance_id: str
    engagement_id: int
    user: Optional[str]


class TaskMetadata(SubjectMetadata):
    task_id: Optional[str]
    resource_id: Optional[str]
    action_type: str


class MonitorMetadata(SubjectMetadata):
    weblink: Optional[AnyHttpUrl] = Field(None, nullable=True)
    plugin_instance_id: int


class BlockSelection(BaseModel):
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
    form_data: FormData


class CaseSubjects(DispatchEnum):
    case = "case"


class IncidentSubjects(DispatchEnum):
    incident = "incident"


class SignalSubjects(DispatchEnum):
    signal = "signal"
    signal_instance = "signal_instance"
