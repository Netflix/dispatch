from typing import Optional, NewType

from pydantic import BaseModel, Field, AnyHttpUrl

from dispatch.enums import DispatchEnum


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
