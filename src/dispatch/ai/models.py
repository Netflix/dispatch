from pydantic import Field

from dispatch.models import DispatchBase
from dispatch.tag.models import TagTypeRecommendation


class TagRecommendations(DispatchBase):
    """
    Model for structured tag recommendations output from AI analysis.

    This model ensures the AI response contains properly structured tag recommendations
    grouped by tag type.
    """

    recommendations: list[TagTypeRecommendation] = Field(
        description="List of tag recommendations grouped by tag type", default_factory=list
    )


class ReadInSummary(DispatchBase):
    """
    Model for structured read-in summary output from AI analysis.

    This model ensures the AI response is properly structured with timeline,
    actions taken, and current status sections.
    """

    timeline: list[str] = Field(
        description="Chronological list of key events and decisions", default_factory=list
    )
    actions_taken: list[str] = Field(
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


class TacticalReport(DispatchBase):
    """
    Model for structured tactical report output from AI analysis. Enforces the presence of fields
    dedicated to the incident's conditions, actions, and needs.
    """

    conditions: str = Field(
        description="Summary of incident circumstances, with focus on scope and impact", default=""
    )
    actions: list[str] = Field(
        description=(
            "Chronological list of actions and analysis by both the party instigating "
            "the incident and the response team"
        ),
        default_factory=list,
    )
    needs: list[str] = Field(
        description=(
            "Identified and unresolved action items from the incident, or an indication "
            "that the incident is at resolution"
        ),
        default_factory=list,
    )


class TacticalReportResponse(DispatchBase):
    """
    Response model for tactical report generation. Includes the structured summary and any error messages.
    """

    tactical_report: TacticalReport | None = None
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
