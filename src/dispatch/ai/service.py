import logging

from dispatch.ai.constants import READ_IN_SUMMARY_CACHE_DURATION
from dispatch.plugins.dispatch_slack.models import IncidentSubjects
import tiktoken
from sqlalchemy.orm import aliased, Session

from dispatch.case.enums import CaseResolutionReason
from dispatch.case.models import Case
from dispatch.enums import Visibility
from dispatch.incident.models import Incident
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.signal import service as signal_service
from dispatch.tag.models import Tag, TagRecommendationResponse
from dispatch.tag_type.models import TagType
from dispatch.case import service as case_service
from dispatch.incident import service as incident_service
from dispatch.types import Subject
from dispatch.event import service as event_service
from dispatch.enums import EventType

from .exceptions import GenAIException
from .models import (
    ReadInSummary,
    ReadInSummaryResponse,
    CaseSignalSummary,
    CaseSignalSummaryResponse,
    TacticalReport,
    TacticalReportResponse,
    TagRecommendations,
)
from .prompt.service import get_by_type
from .enums import AIEventSource, AIEventDescription, GenAIType
from .strings import (
    TAG_RECOMMENDATION_PROMPT,
    TAG_RECOMMENDATION_SYSTEM_MESSAGE,
    INCIDENT_SUMMARY_PROMPT,
    INCIDENT_SUMMARY_SYSTEM_MESSAGE,
    READ_IN_SUMMARY_PROMPT,
    READ_IN_SUMMARY_SYSTEM_MESSAGE,
    SIGNAL_ANALYSIS_PROMPT,
    SIGNAL_ANALYSIS_SYSTEM_MESSAGE,
    STRUCTURED_OUTPUT,
    TACTICAL_REPORT_PROMPT,
    TACTICAL_REPORT_SYSTEM_MESSAGE,
)

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


def prepare_prompt_for_model(prompt: str, model_name: str) -> str:
    """
    Tokenizes and truncates the prompt if it exceeds the model's token limit.
    Returns a prompt string that is safe to send to the model.
    """
    tokenized_prompt, num_tokens, encoding = num_tokens_from_string(prompt, model_name)
    model_token_limit = get_model_token_limit(model_name)
    if num_tokens > model_token_limit:
        prompt = truncate_prompt(tokenized_prompt, num_tokens, encoding, model_token_limit)
    return prompt


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
        # Get the query for cases for a specific resolution reason
        query = signal_service.get_cases_for_signal_by_resolution_reason(
            db_session=db_session,
            signal_id=first_instance_signal.id,
            resolution_reason=resolution_reason,
        )

        # Create an alias for the subquery
        subquery = query.subquery()
        case_alias = aliased(Case, subquery)

        # Filter the cases and extend the related_cases list
        related_cases.extend(db_session.query(case_alias).filter(case_alias.id != case.id).all())

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


def generate_case_signal_summary(case: Case, db_session: Session) -> CaseSignalSummaryResponse:
    """
    Generate an analysis summary of a case stemming from a signal.

    Args:
        case (Case): The case object for which the analysis summary is being generated.
        db_session (Session): The database session used for querying related data.

    Returns:
        CaseSignalSummaryResponse: A structured response containing the analysis summary or error message.
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
    db_prompt = get_by_type(
        genai_type=GenAIType.SIGNAL_ANALYSIS,
        project_id=case.project.id,
        db_session=db_session,
    )
    prompt = f"""
    <prompt>
    {signal_instance.signal.genai_prompt
        if signal_instance.signal.genai_prompt
        else (db_prompt.genai_prompt if db_prompt and db_prompt.genai_prompt else SIGNAL_ANALYSIS_PROMPT)}
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

    prompt = prepare_prompt_for_model(
        prompt, genai_plugin.instance.configuration.chat_completion_model
    )

    # we generate the analysis
    try:
        # Use the system message from the signal if available
        system_message = (
            signal_instance.signal.genai_system_message
            if signal_instance.signal.genai_system_message
            else (
                db_prompt.genai_system_message
                if db_prompt and db_prompt.genai_system_message
                else SIGNAL_ANALYSIS_SYSTEM_MESSAGE
            )
        )

        result = genai_plugin.instance.chat_parse(
            prompt=prompt, response_model=CaseSignalSummary, system_message=system_message
        )

        return CaseSignalSummaryResponse(summary=result)

    except Exception as e:
        log.exception(f"Error generating case signal summary: {e}")
        error_msg = f"Error generating case signal summary: {str(e)}"
        return CaseSignalSummaryResponse(error_message=error_msg)


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

        # Check for enabled prompt in database (type 2 = incident summary)
        db_prompt = get_by_type(
            genai_type=GenAIType.INCIDENT_SUMMARY,
            project_id=incident.project.id,
            db_session=db_session,
        )
        prompt = f"{db_prompt.genai_prompt if db_prompt else INCIDENT_SUMMARY_PROMPT}\n\n{pir_doc}"
        system_message = (
            getattr(db_prompt, "genai_system_message", None) or INCIDENT_SUMMARY_SYSTEM_MESSAGE
        )

        prompt = prepare_prompt_for_model(
            prompt, genai_plugin.instance.configuration.chat_completion_model
        )

        summary = genai_plugin.instance.chat_completion(
            prompt=prompt, system_message=system_message
        )

        incident.summary = summary
        db_session.add(incident)
        db_session.commit()

        # Log the AI summary generation event
        event_service.log_incident_event(
            db_session=db_session,
            source="Dispatch Core App",
            description="AI-generated incident summary created",
            incident_id=incident.id,
            details={"summary": summary},
            type=EventType.other,
        )

        return summary

    except Exception as e:
        log.exception(f"Error trying to generate summary for incident {incident.name}: {e}")
        return "Incident summary not generated. An error occurred."


def get_tag_recommendations(
    *, db_session, project_id: int, case_id: int | None = None, incident_id: int | None = None
) -> TagRecommendationResponse:
    """Gets tag recommendations for a project."""
    genai_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="artificial-intelligence"
    )

    # we check if the artificial intelligence plugin is enabled
    if not genai_plugin:
        message = (
            "AI tag suggestions are not available. No AI plugin is configured for this project."
        )
        log.warning(message)
        return TagRecommendationResponse(recommendations=[], error_message=message)

    # Check for enabled prompt in database (type 1 = tag recommendation)
    db_prompt = get_by_type(
        genai_type=GenAIType.TAG_RECOMMENDATION, project_id=project_id, db_session=db_session
    )
    prompt = db_prompt.genai_prompt if db_prompt else TAG_RECOMMENDATION_PROMPT
    system_message = (
        getattr(db_prompt, "genai_system_message", None) or TAG_RECOMMENDATION_SYSTEM_MESSAGE
    )

    storage_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="storage", project_id=project_id
    )

    # get resources from the case or incident
    resources = ""
    if case_id:
        case = case_service.get(db_session=db_session, case_id=case_id)
        if not case:
            raise ValueError(f"Case with id {case_id} not found")
        if case.visibility == Visibility.restricted:
            message = "AI tag suggestions are not available for restricted cases."
            return TagRecommendationResponse(recommendations=[], error_message=message)

        resources += f"Case title: {case.name}\n"
        resources += f"Description: {case.description}\n"
        resources += f"Resolution: {case.resolution}\n"
        resources += f"Resolution Reason: {case.resolution_reason}\n"
        resources += f"Case type: {case.case_type.name}\n"

        if storage_plugin and case.case_document and case.case_document.resource_id:
            case_doc = storage_plugin.instance.get(
                file_id=case.case_document.resource_id,
                mime_type="text/plain",
            )
            resources += f"Case document: {case_doc}\n"

    elif incident_id:
        incident = incident_service.get(db_session=db_session, incident_id=incident_id)
        if not incident:
            raise ValueError(f"Incident with id {incident_id} not found")
        if incident.visibility == Visibility.restricted:
            message = "AI tag suggestions are not available for restricted incidents."
            return TagRecommendationResponse(recommendations=[], error_message=message)

        resources += f"Incident: {incident.name}\n"
        resources += f"Description: {incident.description}\n"
        resources += f"Resolution: {incident.resolution}\n"
        resources += f"Incident type: {incident.incident_type.name}\n"

        if storage_plugin and incident.incident_document and incident.incident_document.resource_id:
            incident_doc = storage_plugin.instance.get(
                file_id=incident.incident_document.resource_id,
                mime_type="text/plain",
            )
            resources += f"Incident document: {incident_doc}\n"

        if (
            storage_plugin
            and incident.incident_review_document
            and incident.incident_review_document.resource_id
        ):
            incident_review_doc = storage_plugin.instance.get(
                file_id=incident.incident_review_document.resource_id,
                mime_type="text/plain",
            )
            resources += f"Incident review document: {incident_review_doc}\n"

    else:
        raise ValueError("Either case_id or incident_id must be provided")
    # get all tags for the project with the tag_type that has genai_suggestions set to True
    tags: list[Tag] = (
        db_session.query(Tag)
        .filter(Tag.project_id == project_id)
        .filter(Tag.tag_type.has(TagType.genai_suggestions.is_(True)))
        .all()
    )

    # Check if there are any tags available for AI suggestions
    if not tags:
        message = (
            "AI tag suggestions are not available. No tag types are configured "
            "for AI suggestions in this project."
        )
        return TagRecommendationResponse(recommendations=[], error_message=message)

    # add to the resources each tag name, id, tag_type_id, and description
    tag_list = "Tags you can use:\n" + (
        "\n".join(
            [
                f"tag_name: {tag.name}\n"
                f"tag_id: {tag.id}\n"
                f"description: {tag.description}\n"
                f"tag_type_id: {tag.tag_type_id}\n"
                f"tag_type_name: {tag.tag_type.name}\n"
                f"tag_type_description: {tag.tag_type.description}\n"
                for tag in tags
            ]
        )
        + "\n"
    )

    prompt += f"** Tags you can use: {tag_list} \n ** Security event details: {resources}"

    prompt = prepare_prompt_for_model(
        prompt, genai_plugin.instance.configuration.chat_completion_model
    )

    try:
        result = genai_plugin.instance.chat_parse(
            prompt=prompt, response_model=TagRecommendations, system_message=system_message
        )
        return TagRecommendationResponse(recommendations=result.recommendations, error_message=None)
    except Exception as e:
        log.exception(f"Error generating tag recommendations: {e}")
        message = "AI tag suggestions encountered an error. Please try again later."
        return TagRecommendationResponse(recommendations=[], error_message=message)


def generate_read_in_summary(
    *,
    db_session,
    subject: Subject,
    project: Project,
    channel_id: str,
    important_reaction: str,
    participant_email: str = "",
) -> ReadInSummaryResponse:
    """
    Generate a read-in summary for a subject.

    Args:
        subject (Subject): The subject object for which the read-in summary is being generated.
        project (Project): The project context.
        channel_id (str): The channel ID to get conversation from.
        important_reaction (str): The reaction to filter important messages.
        participant_email (str): The email of the participant for whom the summary was generated.

    Returns:
        ReadInSummaryResponse: A structured response containing the read-in summary or error message.
    """
    subject_type = subject.type

    # Check for recent summary event
    if subject_type == IncidentSubjects.incident:
        recent_event = event_service.get_recent_summary_event(
            db_session, incident_id=subject.id, max_age_seconds=READ_IN_SUMMARY_CACHE_DURATION
        )
    else:
        recent_event = event_service.get_recent_summary_event(
            db_session, case_id=subject.id, max_age_seconds=READ_IN_SUMMARY_CACHE_DURATION
        )

    if recent_event and recent_event.details:
        try:
            summary = ReadInSummary(**recent_event.details)
            return ReadInSummaryResponse(summary=summary)
        except Exception as e:
            log.warning(
                f"Failed to parse cached summary from event {recent_event.id}: {e}. Generating new summary."
            )

    # Don't generate if no enabled ai plugin or storage plugin
    genai_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="artificial-intelligence", project_id=project.id
    )
    if not genai_plugin:
        message = f"Read-in summary not generated for {subject.name}. No artificial-intelligence plugin enabled."
        log.warning(message)
        return ReadInSummaryResponse(error_message=message)

    conversation_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="conversation", project_id=project.id
    )
    if not conversation_plugin:
        message = (
            f"Read-in summary not generated for {subject.name}. No conversation plugin enabled."
        )
        log.warning(message)
        return ReadInSummaryResponse(error_message=message)

    conversation = conversation_plugin.instance.get_conversation(
        conversation_id=channel_id, include_user_details=True, important_reaction=important_reaction
    )
    if not conversation:
        message = f"Read-in summary not generated for {subject.name}. No conversation found."
        log.warning(message)
        return ReadInSummaryResponse(error_message=message)

    # Check for enabled prompt in database (type 4 = read-in summary)
    db_prompt = get_by_type(
        genai_type=GenAIType.CONVERSATION_SUMMARY, project_id=project.id, db_session=db_session
    )
    prompt = f"{db_prompt.genai_prompt if db_prompt else READ_IN_SUMMARY_PROMPT}\nConversation messages:\n{conversation}"
    system_message = (
        getattr(db_prompt, "genai_system_message", None) or READ_IN_SUMMARY_SYSTEM_MESSAGE
    ) + STRUCTURED_OUTPUT

    prompt = prepare_prompt_for_model(
        prompt, genai_plugin.instance.configuration.chat_completion_model
    )

    try:
        result = genai_plugin.instance.chat_parse(
            prompt=prompt, response_model=ReadInSummary, system_message=system_message
        )

        # Log the AI read-in summary generation event
        if subject.type == IncidentSubjects.incident:
            # This is an incident
            event_service.log_incident_event(
                db_session=db_session,
                source=AIEventSource.dispatch_genai,
                description=AIEventDescription.read_in_summary_created.format(
                    participant_email=participant_email
                ),
                incident_id=subject.id,
                details=result.dict(),
                type=EventType.other,
            )
        else:
            # This is a case
            event_service.log_case_event(
                db_session=db_session,
                source=AIEventSource.dispatch_genai,
                description=AIEventDescription.read_in_summary_created.format(
                    participant_email=participant_email
                ),
                case_id=subject.id,
                details=result.dict(),
                type=EventType.other,
            )

        return ReadInSummaryResponse(summary=result)

    except Exception as e:
        log.exception(f"Error generating read-in summary: {e}")
        error_msg = f"Error generating read-in summary: {str(e)}"
        return ReadInSummaryResponse(error_message=error_msg)


def generate_tactical_report(
    *,
    db_session,
    incident: Incident,
    project: Project,
    important_reaction: str | None = None,
) -> TacticalReportResponse:
    """
    Generate a tactical report for a given subject.

    Args:
        channel_id (str): The channel ID to target when fetching conversation history
        important_reaction (str): The emoji reaction denoting important messages

    Returns:
        TacticalReportResponse: A structured response containing the tactical report or error message.
    """

    genai_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="artificial-intelligence", project_id=project.id
    )
    if not genai_plugin:
        message = f"Tactical report not generated for {incident.name}. No artificial-intelligence plugin enabled."
        log.warning(message)
        return TacticalReportResponse(error_message=message)

    conversation_plugin = plugin_service.get_active_instance(
        db_session=db_session, plugin_type="conversation", project_id=project.id
    )
    if not conversation_plugin:
        message = (
            f"Tactical report not generated for {incident.name}. No conversation plugin enabled."
        )
        log.warning(message)
        return TacticalReportResponse(error_message=message)

    conversation = conversation_plugin.instance.get_conversation(
        conversation_id=incident.conversation.channel_id,
        include_user_details=True,
        important_reaction=important_reaction,
    )
    if not conversation:
        message = f"Tactical report not generated for {incident.name}. No conversation found."
        log.warning(message)
        return TacticalReportResponse(error_message=message)

    # Check for enabled prompt in database (type 5 = tactical report)
    db_prompt = get_by_type(
        genai_type=GenAIType.TACTICAL_REPORT_SUMMARY, project_id=project.id, db_session=db_session
    )
    raw_prompt = f"{db_prompt.genai_prompt if db_prompt else TACTICAL_REPORT_PROMPT}\nConversation messages:\n{conversation}"
    system_message = (
        getattr(db_prompt, "genai_system_message", None) or TACTICAL_REPORT_SYSTEM_MESSAGE
    ) + STRUCTURED_OUTPUT

    prompt = prepare_prompt_for_model(
        raw_prompt, genai_plugin.instance.configuration.chat_completion_model
    )

    try:
        result = genai_plugin.instance.chat_parse(
            prompt=prompt, response_model=TacticalReport, system_message=system_message
        )

        event_service.log_incident_event(
            db_session=db_session,
            source=AIEventSource.dispatch_genai,
            description=AIEventDescription.tactical_report_created.format(
                incident_name=incident.name
            ),
            incident_id=incident.id,
            details=result.dict(),
            type=EventType.other,
        )

        return TacticalReportResponse(tactical_report=result)

    except Exception as e:
        error_message = f"Error generating tactical report: {str(e)}"
        log.exception(error_message)
        return TacticalReportResponse(error_message=error_message)
