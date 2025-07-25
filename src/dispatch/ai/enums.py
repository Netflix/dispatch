from dispatch.enums import DispatchEnum
from enum import IntEnum


class AIEventSource(DispatchEnum):
    """Source identifiers for AI-generated events."""

    dispatch_genai = "Dispatch GenAI"


class AIEventDescription(DispatchEnum):
    """Description templates for AI-generated events."""

    read_in_summary_created = "AI-generated read-in summary created for {participant_email}"

    tactical_report_created = "AI-generated tactical report created for incident {incident_name}"


class GenAIType(IntEnum):
    """GenAI prompt types for different AI operations."""

    TAG_RECOMMENDATION = 1
    INCIDENT_SUMMARY = 2
    SIGNAL_ANALYSIS = 3
    CONVERSATION_SUMMARY = 4
    TACTICAL_REPORT_SUMMARY = 5
