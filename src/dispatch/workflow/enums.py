from dispatch.enums import DispatchEnum


class WorkflowInstanceStatus(DispatchEnum):
    submitted = "Submitted"
    created = "Created"
    running = "Running"
    completed = "Completed"
    failed = "Failed"
