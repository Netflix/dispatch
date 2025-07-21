from dispatch.enums import DispatchEnum


class AIEventSource(DispatchEnum):
    """Source identifiers for AI-generated events."""

    dispatch_genai = "Dispatch GenAI"


class AIEventDescription(DispatchEnum):
    """Description templates for AI-generated events."""

    read_in_summary_created = "AI-generated read-in summary created for {participant_email}"

    tactical_report_created = "AI-generated tactical report created for incident {incident_name}"
