from dispatch.enums import DispatchEnum


class CanvasType(DispatchEnum):
    """Types of canvases that can be created."""

    summary = "summary"
    tactical_reports = "tactical_reports"
    participants = "participants"
    tasks = "tasks"
