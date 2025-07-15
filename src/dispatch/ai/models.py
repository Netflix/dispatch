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


class CaseSignalSummary(DispatchBase):
    """
    Model for structured case signal summary output from AI analysis.

    This model represents the specific structure expected from the GenAI signal analysis prompt.
    """

    summary: str = Field(
        description="4-5 sentence summary of the security event using precise, factual language",
        default="",
    )
    historical_summary: str = Field(
        description="2-3 sentence summary of historical cases for this signal", default=""
    )
    critical_analysis: str = Field(
        description="Critical analysis considering false positive scenarios", default=""
    )
    recommendation: str = Field(
        description="Recommended next steps based on the analysis", default=""
    )


class CaseSignalSummaryResponse(DispatchBase):
    """
    Response model for case signal summary generation.

    Includes the structured summary and any error messages.
    """

    summary: CaseSignalSummary | None = None
    error_message: str | None = None
