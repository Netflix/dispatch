"""
GenAI Type constants - shared between frontend and backend
"""

from enum import IntEnum


class GenAIType(IntEnum):
    """Enumeration of GenAI prompt types."""

    TAG_RECOMMENDATION = 1
    INCIDENT_SUMMARY = 2
    SIGNAL_ANALYSIS = 3
    CONVERSATION_SUMMARY = 4
    TACTICAL_REPORT_SUMMARY = 5


# Mapping of type IDs to human-readable names
GENAI_TYPES = {
    GenAIType.TAG_RECOMMENDATION: "Tag Recommendation",
    GenAIType.INCIDENT_SUMMARY: "Incident Summary",
    GenAIType.SIGNAL_ANALYSIS: "Signal Analysis",
    GenAIType.CONVERSATION_SUMMARY: "Conversation Summary",
    GenAIType.TACTICAL_REPORT_SUMMARY: "Tactical Report Summary",
}

# Reverse mapping for easy lookup - generated programmatically
GENAI_TYPE_IDS = {name: type_id for type_id, name in GENAI_TYPES.items()}


def get_genai_type_name(type_id: int) -> str:
    """Get the human-readable name for a GenAI type ID."""
    return GENAI_TYPES.get(type_id, f"Unknown Type ({type_id})")


def get_genai_type_id(type_name: str) -> int:
    """Get the type ID for a GenAI type name."""
    return GENAI_TYPE_IDS.get(type_name)


def get_genai_type_options() -> list:
    """Get a list of GenAI type options for forms/dropdowns."""
    return [{"value": type_id, "text": type_name} for type_id, type_name in GENAI_TYPES.items()]
