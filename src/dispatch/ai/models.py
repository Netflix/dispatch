from typing import List
from pydantic import Field

from dispatch.models import DispatchBase


class ReadInSummary(DispatchBase):
    """
    Model for structured read-in summary output from AI analysis.

    This model ensures the AI response is properly structured with timeline,
    actions taken, and current status sections.
    """

    timeline: List[str] = Field(
        description="Chronological list of key events and decisions", default_factory=list
    )
    actions_taken: List[str] = Field(
        description="List of actions that were taken to address the security event",
        default_factory=list,
    )
    current_status: str = Field(
        description="Current status of the security event and any unresolved issues", default=""
    )
    summary: str = Field(description="Overall summary of the security event", default="")


class ReadInSummaryResponse(DispatchBase):
    """
    Response model for read-in summary generation.

    Includes the structured summary and any error messages.
    """

    summary: ReadInSummary | None = None
    error_message: str | None = None
