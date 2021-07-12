from enum import Enum


class TaskStatus(str, Enum):
    open = "Open"
    resolved = "Resolved"


class TaskSource(str, Enum):
    incident = "Incident"
    post_incident_review = "Post Incident Review"


class TaskPriority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
