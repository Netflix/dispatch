from dispatch.enums import DispatchEnum


class WorkflowInstanceStatus(DispatchEnum):
    submitted = "submitted"
    created = "created"
    running = "running"
    completed = "completed"
    failed = "failed"
