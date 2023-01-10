from typing import Optional
from pydantic import BaseModel


class SubjectMetadata(BaseModel):
    id: Optional[str]
    type: Optional[str]
    organization_slug: str = "default"

    project_id: Optional[str]
    channel_id: Optional[str]


class TaskMetadata(SubjectMetadata):
    resource_id: str


class MonitorMetadata(SubjectMetadata):
    weblink: str
    plugin_instance_id: int
