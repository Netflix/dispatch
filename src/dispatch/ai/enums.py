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

    @property
    def display_name(self) -> str:
        """Get the human-friendly display name for the type."""
        display_names = {
            self.TAG_RECOMMENDATION: "Tag Recommendation",
            self.INCIDENT_SUMMARY: "Incident Summary",
            self.SIGNAL_ANALYSIS: "Signal Analysis",
            self.CONVERSATION_SUMMARY: "Conversation Summary",
            self.TACTICAL_REPORT_SUMMARY: "Tactical Report Summary",
        }
        return display_names.get(self, f"Unknown Type ({self.value})")

    @classmethod
    def get_all_types(cls) -> list[dict]:
        """Get all types with their IDs and display names."""
        return [{"id": type_enum.value, "name": type_enum.display_name} for type_enum in cls]
