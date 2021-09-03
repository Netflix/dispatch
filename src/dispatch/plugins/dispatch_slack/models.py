from pydantic import BaseModel


class ButtonValue(BaseModel):
    organization_slug: str = "default"
    incident_id: str
    action_type: str


class TaskButton(ButtonValue):
    resource_id: str


class MonitorButton(ButtonValue):
    weblink: str
