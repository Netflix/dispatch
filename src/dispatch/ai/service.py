import json
import logging

from sqlalchemy.orm import Session

from dispatch.case.enums import CaseResolutionReason
from dispatch.case.models import Case
from dispatch.plugin import service as plugin_service
from dispatch.signal import service as signal_service

from .exceptions import GenAIException

log = logging.getLogger(__name__)


def generate_case_signal_historical_context(case: Case, db_session: Session) -> str:
    """
    Generate historical context for a case stemming from a signal, including related cases and relevant data.

    Args:
        case (Case): The case object for which historical context is being generated.
        db_session (Session): The database session used for querying related data.

    Returns:
        str: A string containing the historical context for the case, or an error message if context generation fails.
    """
    # we fetch the first instance id and signal
    (first_instance_id, first_instance_signal) = signal_service.get_instances_in_case(
        db_session=db_session, case_id=case.id
    ).first()

    signal_instance = signal_service.get_signal_instance(
        db_session=db_session, signal_instance_id=first_instance_id
    )

    # Check if the signal instance is valid
    if not signal_instance:
        message = "Unable to generate historical context. Signal instance not found."
        log.warning(message)
        raise GenAIException(message)

    # Check if the signal is valid
    if not signal_instance.signal:
        message = "Unable to generate historical context. Signal not found."
        log.warning(message)
        raise GenAIException(message)

    # Check if GenAI is enabled for the signal
    if not signal_instance.signal.genai_enabled:
        message = (
            "Unable to generate historical context. GenAI feature not enabled for this detection."
        )
        log.warning(message)
        raise GenAIException(message)

    # we fetch related cases
    related_cases = []
    for resolution_reason in CaseResolutionReason:
        related_cases.extend(
            signal_service.get_cases_for_signal_by_resolution_reason(
                db_session=db_session,
                signal_id=first_instance_signal.id,
                resolution_reason=resolution_reason,
            )
            .from_self()  # NOTE: function deprecated in SQLAlchemy 1.4 and removed in 2.0
            .filter(Case.id != case.id)
        )

    # we prepare historical context
    historical_context = []
    for related_case in related_cases:
        historical_context.append("<case>")
        historical_context.append(f"<case_name>{related_case.name}</case_name>")
        historical_context.append(f"<case_resolution>{related_case.resolution}</case_resolution")
        historical_context.append(
            f"<case_resolution_reason>{related_case.resolution_reason}</case_resolution_reason>"
        )
        historical_context.append(
            f"<case_alert_data>{related_case.signal_instances[0].raw}</case_alert_data>"
        )
        conversation_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=case.project.id, plugin_type="conversation"
        )
        if conversation_plugin:
            if related_case.conversation and related_case.conversation.channel_id:
                # we fetch conversation replies for the related case
                conversation_replies = conversation_plugin.instance.get_conversation_replies(
                    conversation_id=related_case.conversation.channel_id,
                    thread_ts=related_case.conversation.thread_id,
                )
                for reply in conversation_replies:
                    historical_context.append(
                        f"<case_conversation_reply>{reply}</case_conversation_reply>"
                    )
        else:
            log.warning(
                "Conversation replies not included in historical context. No conversation plugin enabled."
            )
        historical_context.append("</case>")

    return "\n".join(historical_context)


def generate_case_signal_summary(case: Case, db_session: Session) -> dict[str, str]:
    """
    Generate an analysis summary of a case stemming from a signal.

    Args:
        case (Case): The case object for which the analysis summary is being generated.
        db_session (Session): The database session used for querying related data.

    Returns:
        dict: A dictionary containing the analysis summary, or an error message if the summary generation fails.
    """
    # we generate the historical context
    try:
        historical_context = generate_case_signal_historical_context(
            case=case, db_session=db_session
        )
    except GenAIException as e:
        log.warning(f"Error generating GenAI historical context for {case.name}: {str(e)}")
        raise e

    # we fetch the artificial intelligence plugin
    genai_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="artificial-intelligence"
    )

    # we check if the artificial intelligence plugin is enabled
    if not genai_plugin:
        message = (
            "Unable to generate GenAI signal analysis. No artificial-intelligence plugin enabled."
        )
        log.warning(message)
        raise GenAIException(message)

    # we fetch the first instance id and signal
    (first_instance_id, first_instance_signal) = signal_service.get_instances_in_case(
        db_session=db_session, case_id=case.id
    ).first()

    signal_instance = signal_service.get_signal_instance(
        db_session=db_session, signal_instance_id=first_instance_id
    )

    # Check if the signal instance is valid
    if not signal_instance:
        message = "Unable to generate GenAI signal analysis. Signal instance not found."
        log.warning(message)
        raise GenAIException(message)

    # Check if the signal is valid
    if not signal_instance.signal:
        message = "Unable to generate GenAI signal analysis. Signal not found."
        log.warning(message)
        raise GenAIException(message)

    # Check if GenAI is enabled for the signal
    if not signal_instance.signal.genai_enabled:
        message = f"Unable to generate GenAI signal analysis. GenAI feature not enabled for {signal_instance.signal.name}."
        log.warning(message)
        raise GenAIException(message)

    # we check if the signal has a prompt defined
    if not signal_instance.signal.genai_prompt:
        message = f"Unable to generate GenAI signal analysis. No GenAI prompt defined for {signal_instance.signal.name}."
        log.warning(message)
        raise GenAIException(message)

    # we generate the analysis
    response = genai_plugin.instance.chat_completion(
        prompt=f"""

        <prompt>
        {signal_instance.signal.genai_prompt}
        </prompt>

        <current_event>
        {str(signal_instance.raw)}
        </current_event>

        <runbook>
        {signal_instance.signal.runbook}
        </runbook>

        <historical_context>
        {historical_context}
        </historical_context>

        """
    )

    try:
        summary = json.loads(
            response["choices"][0]["message"]["content"]
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        # we check if the summary is empty
        if not summary:
            message = "Unable to generate GenAI signal analysis. We received an empty response from the artificial-intelligence plugin."
            log.warning(message)
            raise GenAIException(message)

        return summary
    except json.JSONDecodeError as e:
        message = "Unable to generate GenAI signal analysis. Error decoding response from the artificial-intelligence plugin."
        log.warning(message)
        raise GenAIException(message) from e
