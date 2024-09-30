import logging
from typing import NamedTuple

from blockkit import (
    Actions,
    Button,
    Context,
    Divider,
    Message,
    Section,
)
from blockkit.surfaces import Block
from slack_sdk.errors import SlackApiError
from slack_sdk.web.client import WebClient
from sqlalchemy.orm import Session

from dispatch.case.enums import CaseStatus
from dispatch.case.models import Case
from dispatch.config import DISPATCH_UI_URL
from dispatch.messaging.strings import CASE_STATUS_DESCRIPTIONS, CASE_VISIBILITY_DESCRIPTIONS
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseNotificationActions,
    SignalEngagementActions,
    SignalNotificationActions,
)
from dispatch.plugins.dispatch_slack.config import MAX_SECTION_TEXT_LENGTH
from dispatch.plugins.dispatch_slack.models import (
    CaseSubjects,
    EngagementMetadata,
    SignalSubjects,
    SubjectMetadata,
)
from dispatch.signal import service as signal_service
from dispatch.signal.enums import SignalEngagementStatus
from dispatch.signal.models import (
    SignalEngagement,
    SignalInstance,
)

log = logging.getLogger(__name__)


def map_priority_color(color: str) -> str:
    """Maps a priority color to its corresponding emoji symbol."""
    if not color:
        return ""

    # TODO we should probably restrict the possible colors to make this work
    priority_color_mapping = {
        "#9e9e9e": "⚪",
        "#8bc34a": "🟢",
        "#ffeb3b": "🟡",
        "#ff9800": "🟠",
        "#f44336": "🔴",
        "#9c27b0": "🟣",
    }

    return priority_color_mapping.get(color.lower(), "")


def create_case_message(case: Case, channel_id: str) -> list[Block]:
    """
    Creates a Slack message for a given case.

    Args:
        case (Case): The case object containing details to be included in the message.
        channel_id (str): The ID of the Slack channel where the message will be sent.

    Returns:
        list[Block]: A list of Block objects representing the structure of the Slack message.
    """
    priority_color = map_priority_color(color=case.case_priority.color)

    title_prefix = "*Detection*" if case.signal_instances else "*Title*"
    title = f"{title_prefix} \n {case.title}."

    fields = [
        f"*Assignee* \n {case.assignee.individual.email}",
        f"*Status* \n {case.status}",
        f"*Case Type* \n {case.case_type.name}",
        f"*Case Priority* \n {priority_color} {case.case_priority.name}",
    ]

    if case.signal_instances:
        if variant := case.signal_instances[0].signal.variant:
            fields.append(f"*Variant* \n {variant}")

    blocks = [
        Section(
            text=title,
            accessory=Button(
                text="View in Dispatch",
                action_id="button-link",
                url=f"{DISPATCH_UI_URL}/{case.project.organization.slug}/cases/{case.name}",
            ),
        ),
        Section(text=f"*Description* \n {case.description}"),
        Section(fields=fields),
        Section(text="*Actions*"),
    ]

    button_metadata = SubjectMetadata(
        type=CaseSubjects.case,
        organization_slug=case.project.organization.slug,
        id=case.id,
        project_id=case.project.id,
        channel_id=channel_id,
    ).json()

    if case.has_channel:
        action_buttons = [
            Button(text=":slack: Case Channel", style="primary", url=case.conversation.weblink if case.conversation else "")
        ]
        blocks.extend([Actions(elements=action_buttons)])
    elif case.status == CaseStatus.escalated:
        blocks.extend(
            [
                Actions(
                    elements=[
                        Button(
                            text=":siren: Join Incident",
                            action_id=CaseNotificationActions.join_incident,
                            style="primary",
                            value=button_metadata,
                        )
                    ]
                )
            ]
        )
    elif case.status == CaseStatus.closed:
        blocks.extend(
            [
                Section(text=f"*Resolution reason* \n {case.resolution_reason}"),
                Section(
                    text=f"*Resolution description* \n {case.resolution}"[:MAX_SECTION_TEXT_LENGTH]
                ),
                Actions(
                    elements=[
                        Button(
                            text="Re-open",
                            action_id=CaseNotificationActions.reopen,
                            style="primary",
                            value=button_metadata,
                        )
                    ]
                ),
            ]
        )
    else:
        action_buttons = [
            Button(
                text=":resolved: Resolve",
                action_id=CaseNotificationActions.resolve,
                style="primary",
                value=button_metadata,
            ),
            Button(
                text=":modified: Edit",
                action_id=CaseNotificationActions.edit,
                value=button_metadata,
            ),
            Button(
                text=":slack: Create Channel",
                action_id=CaseNotificationActions.migrate,
                value=button_metadata,
            ),
            Button(
                text=":fire: Escalate",
                action_id=CaseNotificationActions.escalate,
                style="danger",
                value=button_metadata,
            ),
        ]
        if case.status == CaseStatus.new:
            action_buttons.insert(
                0,
                Button(
                    text=":mag: Triage",
                    action_id=CaseNotificationActions.triage,
                    style="primary",
                    value=button_metadata,
                ),
            )
        blocks.extend([Actions(elements=action_buttons)])

    return Message(blocks=blocks).build()["blocks"]


class EntityGroup(NamedTuple):
    value: str
    related_case_count: int


def create_signal_messages(case_id: int, channel_id: str, db_session: Session) -> list[Message]:
    """
    Creates signal messages for a given case.

    Args:
        case_id (int): The ID of the case for which to create signal messages.
        channel_id (str): The ID of the Slack channel where the message will be sent.
        db_session (Session): The database session to use for querying signal instances.

    Returns:
        list[Message]: A list of Message objects representing the structure of the Slack messages.
    """
    instances = signal_service.get_instances_in_case(db_session=db_session, case_id=case_id)
    (first_instance_id, first_instance_signal) = instances.first()

    organization_slug = first_instance_signal.project.organization.slug
    project_id = first_instance_signal.project.id
    button_metadata = SubjectMetadata(
        type=SignalSubjects.signal_instance,
        organization_slug=organization_slug,
        id=str(first_instance_id),
        project_id=project_id,
        channel_id=channel_id,
    ).json()

    elements = []

    # Check if `first_instance_signal.external_url` is not empty
    if first_instance_signal.external_url:
        # If `first_instance_signal.external_url` is not empty, add the "Response Plan" button
        elements.append(
            Button(
                text="🔖 Response Plan",
                action_id="button-link",
                url=first_instance_signal.external_url,
            )
        )

    # Define the initial elements with "Raw Data" and "Snooze" buttons
    elements.append(
        Button(
            text="💤 Snooze Alerts",
            action_id=SignalNotificationActions.snooze,
            value=button_metadata,
        )
    )

    # Create the Actions block with the elements
    signal_metadata_blocks = [
        Section(text="*Actions*"),
        Actions(elements=elements)
    ]

    return Message(blocks=signal_metadata_blocks).build()["blocks"]


def create_genai_signal_summary(
    case: Case,
    channel_id: str,
    db_session: Session,
    client: WebClient,
) -> list[Block]:
    """
    Creates a signal summary using a generative AI plugin.

    This function generates a summary for a given case by leveraging historical context and
    a generative AI plugin. It fetches related cases, their resolutions, and relevant Slack
    messages to provide a comprehensive summary.

    Args:
        case (Case): The case object containing details to be included in the summary.
        channel_id (str): The ID of the Slack channel where the summary will be sent.
        db_session (Session): The database session to use for querying signal instances and related cases.
        client (WebClient): The Slack WebClient to fetch threaded messages.

    Returns:
        list[Block]: A list of Block objects representing the structure of the Slack message.
    """
    signal_metadata_blocks: list[Block] = []

    (first_instance_id, first_instance_signal) = signal_service.get_instances_in_case(db_session=db_session, case_id=case.id).first()

    if not first_instance_id or not first_instance_signal:
        log.warning("Unable to generate GenAI signal summary. No signal instances found.")
        return signal_metadata_blocks

    # Fetch related cases
    related_cases = (
        signal_service.get_cases_for_signal(
            db_session=db_session, signal_id=first_instance_signal.id
        )
        .from_self() # NOTE: function deprecated in SQLAlchemy 1.4 and removed in 2.0
        .filter(Case.id != case.id)
    )

    # Prepare historical context
    historical_context = []
    for related_case in related_cases:
        historical_context.append("<case>")
        historical_context.append(f"<case_name>{related_case.name}</case_name>")
        historical_context.append(f"<resolution>{related_case.resolution}</resolution")
        historical_context.append(f"<resolution_reason>{related_case.resolution_reason}</resolution_reason>")

        # Fetch Slack messages for the related case
        if related_case.conversation and related_case.conversation.channel_id:
            try:
                # Fetch threaded messages
                thread_messages = client.conversations_replies(
                    channel=related_case.conversation.channel_id,
                    ts=related_case.conversation.thread_id,
                )

                # Add relevant messages to the context (e.g., first 5 messages)
                for message in thread_messages["messages"][:5]:
                    historical_context.append(f"<slack_message>{message['text']}</slack_message>")
            except SlackApiError as e:
                log.error(f"Error fetching Slack messages for case {related_case.name}: {e}")

        historical_context.append("</case>")

    historical_context_str = "\n".join(historical_context)

    signal_instance = signal_service.get_signal_instance(
        db_session=db_session, signal_instance_id=first_instance_id
    )

    genai_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="artificial-intelligence"
    )

    if not genai_plugin:
        log.warning("Unable to generate GenAI signal summary. No artificial-intelligence plugin enabled.")
        return signal_metadata_blocks

    if not signal_instance.signal.genai_prompt:
        log.warning(f"Unable to generate GenAI signal summary. No GenAI prompt defined for {signal_instance.signal.name}")
        return signal_metadata_blocks

    response = genai_plugin.instance.chat_completion(
        prompt=f"""

        <prompt>
        {signal_instance.signal.genai_prompt}
        </prompt>

        <current_event>
        {str(signal_instance.raw)}
        </current_event>

        <historical_context>
        {historical_context_str}
        </historical_context>

        <runbook>
        {first_instance_signal.runbook}
        </runbook>
        """
    )
    message = response["choices"][0]["message"]["content"]

    signal_metadata_blocks.append(
        Section(text=f"*GenAI Alert Summary*\n\n{message}")
    )

    return Message(blocks=signal_metadata_blocks).build()["blocks"]


def create_signal_engagement_message(
    case: Case,
    channel_id: str,
    engagement: SignalEngagement,
    signal_instance: SignalInstance,
    user_email: str,
    engagement_status: SignalEngagementStatus = SignalEngagementStatus.new,
) -> list[Block]:
    """
    Generate a list of blocks for a signal engagement message.

    Args:
        case (Case): The case object related to the signal instance.
        channel_id (str): The ID of the Slack channel where the message will be sent.
        message (str): Additional context information to include in the message.
        signal_instance (SignalInstance): The signal instance object related to the engagement.
        user_email (str): The email of the user being engaged.
        engagement (SignalEngagement): The engagement object.

    Returns:
        list[Block]: A list of blocks representing the message structure for the engagement message.
    """
    button_metadata = EngagementMetadata(
        id=case.id,
        type=CaseSubjects.case,
        organization_slug=case.project.organization.slug,
        project_id=case.project.id,
        channel_id=channel_id,
        signal_instance_id=str(signal_instance.id),
        engagement_id=engagement.id,
        user=user_email,
    ).json()

    username, _ = user_email.split("@")
    blocks = [
        Section(text=f"@{username}, we could use your help to resolve this case. Please, see additional context below:"),
        Section(
            text=f"{engagement.message if engagement.message else 'No context provided for this alert.'}"
        ),
    ]

    if engagement_status == SignalEngagementStatus.new:
        blocks.extend(
            [
                Section(text="Can you please confirm this was you and whether the behavior was expected?"),
                Actions(
                    elements=[
                        Button(
                            text="Confirm",
                            style="primary",
                            action_id=SignalEngagementActions.approve,
                            value=button_metadata,
                        ),
                        Button(
                            text="Deny",
                            style="danger",
                            action_id=SignalEngagementActions.deny,
                            value=button_metadata,
                        ),
                    ]
                ),
            ]
        )

    elif engagement_status == SignalEngagementStatus.approved:
        blocks.extend(
            [
                Section(text=f":white_check_mark: @{username} confirmed the behavior as expected."),
            ]
        )
    else:
        blocks.extend(
            [
                Section(text=":warning: @{username} denied the behavior as expected. Please investigate the case and escalate to incident if necessary."),
            ]
        )

    return Message(blocks=blocks).build()["blocks"]


def create_welcome_ephemeral_message_to_participant(case: Case) -> list[Block]:
    blocks = [
        Section(
            text="You've been added to this case, because we think you may be able to help resolve it. Please, review the case details below and reach out to the case assignee if you have any questions.",
        ),
        Section(
            text=f"*Title* \n {case.title}",
        ),
        Section(
            text=f"*Description* \n {case.description}",
        ),
        Section(
            text=f"*Visibility - {case.visibility}* \n {CASE_VISIBILITY_DESCRIPTIONS[case.visibility]}",
        ),
        Section(
            text=f"*Status - {case.status}* \n {CASE_STATUS_DESCRIPTIONS[case.status]}",
        ),
        Section(
            text=f"*Type - {case.case_type.name}* \n {case.case_type.description}",
        ),
        Section(
            text=f"*Severity - {case.case_severity.name}* \n {case.case_severity.description}",
        ),
        Section(
            text=f"*Priority - {case.case_priority.name}* \n {case.case_priority.description}",
        ),
        Section(
            text=f"*Assignee - {case.assignee.individual.name}*",
        ),
        Section(
            text=f"*Reporter - {case.reporter.individual.name}*",
        ),
    ]
    return Message(blocks=blocks).build()["blocks"]


def create_case_thread_migration_message(channel_weblink: str) -> list[Block]:
    blocks = [
        Context(
            elements=[
                f"This conversation has been migrated to a dedicated Case channel. All future updates and discussions will take place <{channel_weblink}|here>."
            ]
        ),
        Divider(),
    ]

    return Message(blocks=blocks).build()["blocks"]


def create_case_channel_migration_message(thread_weblink: str) -> list[Block]:
    blocks = [
        Context(
            elements=[
                f"Migrated Case conversation from the <{thread_weblink}|original Case thread>."
            ]
        ),
        Divider(),
    ]

    return Message(blocks=blocks).build()["blocks"]
