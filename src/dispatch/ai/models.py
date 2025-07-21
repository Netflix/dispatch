from typing import List
from pydantic import Field
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint

from dispatch.models import DispatchBase
from dispatch.database.core import Base
from dispatch.models import TimeStampMixin, ProjectMixin, Pagination, PrimaryKey
from dispatch.project.models import ProjectRead


class Prompt(Base, TimeStampMixin, ProjectMixin):
    """
    SQLAlchemy model for AI prompts.

    This model stores AI prompts that can be used for various GenAI operations
    like tag recommendations, incident summaries, etc.
    """

    # Columns
    id = Column(Integer, primary_key=True)
    genai_type = Column(Integer, nullable=False)
    genai_prompt = Column(String, nullable=False)
    genai_system_message = Column(String, nullable=True)
    enabled = Column(Boolean, default=False, nullable=False)


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


class TacticalReport(DispatchBase):
    """
    Model for structured tactical report output from AI analysis. Enforces the presence of fields
    dedicated to the incident's conditions, actions, and needs.
    """

    conditions: str = Field(
        description="Summary of incident circumstances, with focus on scope and impact", default=""
    )
    actions: str | list[str] = Field(
        description=(
            "Chronological list of actions and analysis by both the party instigating "
            "the incident and the response team"
        ),
        default_factory=list,
    )
    needs: str | list[str] = Field(
        description=(
            "Identified and unresolved action items from the incident, or an indication "
            "that the incident is at resolution"
        ),
        default="",
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


# AI Prompt Models
class PromptBase(DispatchBase):
    """
    Base Pydantic model for AI prompts.

    This model defines the core fields for AI prompts that can be used
    for various GenAI operations like tag recommendations, incident summaries, etc.
    """

    genai_type: int = Field(
        description="The type of GenAI prompt (1=Tag Recommendation, 2=Incident Summary, etc.)"
    )
    genai_prompt: str = Field(description="The main prompt template to send to the AI model")
    genai_system_message: str | None = Field(
        default=None, description="The system message to set the behavior of the AI assistant"
    )
    enabled: bool = Field(
        default=False, description="Whether this prompt is active and available for use"
    )


class PromptCreate(PromptBase):
    """
    Model for creating a new AI prompt.

    Inherits all fields from PromptBase.
    """

    pass


class PromptUpdate(DispatchBase):
    """
    Model for updating an existing AI prompt.

    All fields are optional to allow partial updates.
    """

    genai_type: int | None = Field(
        default=None,
        description="The type of GenAI prompt (1=Tag Recommendation, 2=Incident Summary, etc.)",
    )
    genai_prompt: str | None = Field(
        default=None, description="The main prompt template to send to the AI model"
    )
    genai_system_message: str | None = Field(
        default=None, description="The system message to set the behavior of the AI assistant"
    )
    enabled: bool | None = Field(
        default=None, description="Whether this prompt is active and available for use"
    )


class PromptRead(PromptBase):
    """
    Model for reading AI prompt data.

    Includes all base fields plus metadata fields.
    """

    id: PrimaryKey = Field(description="Unique identifier for the prompt")
    created_at: str = Field(description="ISO timestamp when the prompt was created")
    updated_at: str = Field(description="ISO timestamp when the prompt was last updated")
    project: ProjectRead = Field(description="Project this prompt belongs to")


class PromptPagination(Pagination):
    """Pagination model for AI prompts."""

    items: list[PromptRead]
