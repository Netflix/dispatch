from typing import Optional
from pydantic import BaseModel


class SubjectMetadata(BaseModel):
    id: Optional[str]
    type: Optional[str]
    organization_slug: str = "default"

    project_id: Optional[str]
    channel_id: Optional[str]


class TaskMetadata(SubjectMetadata):
    task_id: Optional[str]
    resource_id: Optional[str]
    action_type: str


class MonitorMetadata(SubjectMetadata):
    weblink: str
    plugin_instance_id: int


class SubjectMetadata(BaseModel):
    id: Optional[str]
    type: Optional[str]
    organization_slug: str = "default"

    project_id: Optional[str]
    channel_id: Optional[str]
