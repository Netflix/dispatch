import json
import logging

import tiktoken
from sqlalchemy.orm import Session

from dispatch.case.enums import CaseResolutionReason
from dispatch.case.models import Case
from dispatch.enums import Visibility
from dispatch.incident.models import Incident
from dispatch.plugin import service as plugin_service
from dispatch.signal import service as signal_service

from .exceptions import GenAIException

log = logging.getLogger(__name__)


def get_model_token_limit(model_name: str, buffer_percentage: float = 0.05) -> int:
    """
    Returns the maximum token limit for a given LLM model with a safety buffer.

    Args:
        model_name (str): The name of the LLM model.
        buffer_percentage (float): Percentage of tokens to reserve as buffer (default: 5%).

    Returns:
        int: The maximum number of tokens allowed in the context window for the specified model,
             with a safety buffer applied.
    """
    default_max_tokens = 128000

    model_token_limits = {
        # OpenAI models (most recent)
        "gpt-4o": 128000,
        # Anthropic models (Claude 3.5 and 3.7 Sonnet variants)
        "claude-3-5-sonnet-20241022": 200000,
        "claude-3-7-sonnet-20250219": 200000,
    }

    # Get the raw token limit for the model
    raw_limit = model_token_limits.get(model_name.lower(), default_max_tokens)

    # Apply safety buffer
    safe_limit = int(raw_limit * (1 - buffer_percentage))

    return safe_limit


def num_tokens_from_string(message: str, model: str) -> tuple[list[int], int, tiktoken.Encoding]:
    """
    Calculate the number of tokens in a given string for a specified model.

    Args:
        message (str): The input string to be tokenized.
        model (str): The model name to use for tokenization.

    Returns:
        tuple: A tuple containing a list of token integers, the number of tokens, and the encoding object.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        log.warning(
            f"We could not automatically map {model} to a tokeniser. Using o200k_base encoding."
        )
        # defaults to o200k_base encoding used in gpt-4o, gpt-4o-mini models
        encoding = tiktoken.get_encoding("o200k_base")

    tokenized_message = encoding.encode(message)
    num_tokens = len(tokenized_message)

    return tokenized_message, num_tokens, encoding


def truncate_prompt(
    tokenized_prompt: list[int],
    num_tokens: int,
    encoding: tiktoken.Encoding,
    model_token_limit: int,
) -> str:
    """
    Truncate the tokenized prompt to ensure it does not exceed the maximum number of tokens.

    Args:
        tokenized_prompt (list[int]): The tokenized input prompt to be truncated.
        num_tokens (int): The number of tokens in the input prompt.
        encoding (tiktoken.Encoding): The encoding object used for tokenization.

    Returns:
        str: The truncated prompt as a string.
    """
    excess_tokens = num_tokens - model_token_limit
    truncated_tokenized_prompt = tokenized_prompt[:-excess_tokens]
    truncated_prompt = encoding.decode(truncated_tokenized_prompt)
    log.warning(f"GenAI prompt truncated to fit within {model_token_limit} tokens.")
    return truncated_prompt


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

    # we generate the prompt
    prompt = f"""
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

    tokenized_prompt, num_tokens, encoding = num_tokens_from_string(
        prompt, genai_plugin.instance.configuration.chat_completion_model
    )

    # we check if the prompt exceeds the token limit
    model_token_limit = get_model_token_limit(
        genai_plugin.instance.configuration.chat_completion_model
    )
    if num_tokens > model_token_limit:
        prompt = truncate_prompt(tokenized_prompt, num_tokens, encoding, model_token_limit)

    # we generate the analysis
    response = genai_plugin.instance.chat_completion(prompt=prompt)

    try:
        summary = json.loads(response.replace("```json", "").replace("```", "").strip())

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


def generate_incident_summary(incident: Incident, db_session: Session) -> str:
    """
    Generate a summary for an incident.

    Args:
        incident (Incident): The incident object for which the summary is being generated.
        db_session (Session): The database session used for querying related data.

    Returns:
        str: A string containing the summary of the incident, or an error message if summary generation fails.
    """
    # Skip summary for restricted incidents
    if incident.visibility == Visibility.restricted:
        return "Incident summary not generated for restricted incident."

    # Skip if incident is a duplicate
    if incident.duplicates:
        return "Incident summary not generated for duplicate incident."

    # Skip if no incident review document
    if not incident.incident_review_document or not incident.incident_review_document.resource_id:
        log.info(
            f"Incident summary not generated for incident {incident.name}. No review document found."
        )
        return "Incident summary not generated. No review document found."

    # Don't generate if no enabled ai plugin or storage plugin
    genai_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="artificial-intelligence", project_id=incident.project.id
    )
    if not genai_plugin:
        message = f"Incident summary not generated for incident {incident.name}. No artificial-intelligence plugin enabled."
        log.warning(message)
        return "Incident summary not generated. No artificial-intelligence plugin enabled."

    storage_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="storage", project_id=incident.project.id
    )

    if not storage_plugin:
        log.info(
            f"Incident summary not generated for incident {incident.name}. No storage plugin enabled."
        )
        return "Incident summary not generated. No storage plugin enabled."

    try:
        pir_doc = storage_plugin.instance.get(
            file_id=incident.incident_review_document.resource_id,
            mime_type="text/plain",
        )
        prompt = f"""
            Given the text of the security post-incident review document below,
            provide answers to the following questions in a paragraph format.
            Do not include the questions in your response.
            Do not use any of these words in your summary unless they appear in the document: breach, unauthorized, leak, violation, unlawful, illegal.
            1. What is the summary of what happened?
            2. What were the overall risk(s)?
            3. How were the risk(s) mitigated?
            4. How was the incident resolved?
            5. What are the follow-up tasks?

            {pir_doc}
        """

        tokenized_prompt, num_tokens, encoding = num_tokens_from_string(
            prompt, genai_plugin.instance.configuration.chat_completion_model
        )

        # we check if the prompt exceeds the token limit
        model_token_limit = get_model_token_limit(
            genai_plugin.instance.configuration.chat_completion_model
        )
        if num_tokens > model_token_limit:
            prompt = truncate_prompt(tokenized_prompt, num_tokens, encoding, model_token_limit)

        summary = genai_plugin.instance.chat_completion(prompt=prompt)

        incident.summary = summary
        db_session.add(incident)
        db_session.commit()

        return summary

    except Exception as e:
        log.exception(f"Error trying to generate summary for incident {incident.name}: {e}")
        return "Incident summary not generated. An error occurred."
