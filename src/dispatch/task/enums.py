from dispatch.enums import DispatchEnum


class TaskStatus(DispatchEnum):
    open = "Open"
    resolved = "Resolved"


class TaskSource(DispatchEnum):
    incident = "Incident"
    post_incident_review = "Post Incident Review"


class TaskPriority(DispatchEnum):
    low = "Low"
    medium = "Medium"
    high = "High"
