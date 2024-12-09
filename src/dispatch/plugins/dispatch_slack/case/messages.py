import logging
from typing import NamedTuple, Tuple

from blockkit import (
    Actions,
    Button,
    Context,
    Divider,
    Message,
    Section,
)
from blockkit.surfaces import Block
from sqlalchemy.orm import Session

from dispatch.ai import service as ai_service
from dispatch.ai.exceptions import GenAIException
from dispatch.case import service as case_service
from dispatch.case.enums import CaseStatus
from dispatch.case.models import Case
from dispatch.config import DISPATCH_UI_URL
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseNotificationActions,
    SignalEngagementActions,
    SignalNotificationActions,
)
from dispatch.plugins.dispatch_slack.config import (
    MAX_SECTION_TEXT_LENGTH,
)
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
            Button(
                text=":slack: Case Channel",
                style="primary",
                url=case.conversation.weblink if case.conversation else "",
            )
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
                text=":white_check_mark: Resolve",
                action_id=CaseNotificationActions.resolve,
                value=button_metadata,
            ),
            Button(
                text=":pencil: Edit",
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
                value=button_metadata,
            ),
        ]
        if case.status == CaseStatus.new:
            action_buttons.insert(
                0,
                Button(
                    text=":mag: Triage",
                    action_id=CaseNotificationActions.triage,
                    value=button_metadata,
                ),
            )
        blocks.extend([Actions(elements=action_buttons)])

    return Message(blocks=blocks).build()["blocks"]


class EntityGroup(NamedTuple):
    value: str
    related_case_count: int


def create_signal_message(case_id: int, channel_id: str, db_session: Session) -> list[Message]:
    """
    Creates a signal message for a given case.

    This function generates a signal message for a specific case by fetching the first signal instance
    associated with the case and creating metadata blocks for the message.

    Args:
        case_id (int): The ID of the case for which to create the signal message.
        channel_id (str): The ID of the Slack channel where the message will be sent.
        db_session (Session): The database session to use for querying signal instances.

    Returns:
        list[Message]: A list of Message objects representing the structure of the Slack messages.
    """
    # we fetch the first instance to get the organization slug and project id
    instances = signal_service.get_instances_in_case(db_session=db_session, case_id=case_id)
    (first_instance_id, first_instance_signal) = instances.first()

    case = case_service.get(db_session=db_session, case_id=case_id)

    # we create the signal metadata blocks
    signal_metadata_blocks = [
        Section(text="*Alerts*"),
        Section(
            text=f"We observed <{DISPATCH_UI_URL}/{first_instance_signal.project.organization.slug}/cases/{case.name}/signal/{first_instance_id}|{instances.count()} alert(s)> in this case. The first alert for this case can be seen below."
        ),
    ]

    return Message(blocks=signal_metadata_blocks).build()["blocks"]


def create_action_buttons_message(
    case: Case, channel_id: str, db_session: Session
) -> list[Message]:
    """
    Creates a message with action buttons for a given case.

    This function generates a message containing action buttons for a specific case by fetching the first signal instance
    associated with the case and creating metadata blocks for the message.

    Args:
        case_id (int): The ID of the case for which to create the action buttons message.
        channel_id (str): The ID of the Slack channel where the message will be sent.
        db_session (Session): The database session to use for querying signal instances.

    Returns:
        list[Message]: A list of Message objects representing the structure of the Slack messages.
    """
    # we fetch the first instance to get the organization slug and project id
    instances = signal_service.get_instances_in_case(db_session=db_session, case_id=case.id)
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
    mfa_button_metadata = SubjectMetadata(
        type=CaseSubjects.case,
        organization_slug=organization_slug,
        id=case.id,
        project_id=project_id,
        channel_id=channel_id,
    ).json()

    # we create the response plan and the snooze buttons
    elements = []

    if first_instance_signal.external_url:
        elements.append(
            Button(
                text="🔖 View Response Plan",
                action_id="button-link",
                url=first_instance_signal.external_url,
            )
        )

    elements.extend(
        [
            Button(
                text="💤 Snooze Alert",
                action_id=SignalNotificationActions.snooze,
                value=button_metadata,
            ),
            Button(
                text="👤 User MFA Challenge",
                action_id=CaseNotificationActions.user_mfa,
                value=mfa_button_metadata,
            ),
        ]
    )

    # we create the signal metadata blocks
    signal_metadata_blocks = [
        Divider(),
        Section(text="*Actions*"),
        Actions(elements=elements),
        Divider(),
    ]

    return Message(blocks=signal_metadata_blocks).build()["blocks"]


def json_to_slack_format(json_message: dict[str, str]) -> str:
    """
    Converts a JSON dictionary to Slack markup format.

    Args:
        json_dict (dict): The JSON dictionary to convert.

    Returns:
        str: A string formatted with Slack markup.
    """
    slack_message = ""
    for key, value in json_message.items():
        slack_message += f"*{key}*\n{value}\n\n"
    return slack_message.strip()


def create_genai_signal_message_metadata_blocks(
    signal_metadata_blocks: list[Block], message: str | dict[str, str]
) -> list[Block]:
    """
    Appends a GenAI signal analysis section to the signal metadata blocks.

    Args:
        signal_metadata_blocks (list[Block]): The list of existing signal metadata blocks.
        message (str | dict[str, str]): The GenAI analysis message, either as a string or a dictionary.

    Returns:
        list[Block]: The updated list of signal metadata blocks with the GenAI analysis section appended.
    """
    if isinstance(message, dict):
        message = json_to_slack_format(message)
    signal_metadata_blocks.append(
        Section(text=f":magic_wand: *GenAI Alert Analysis*\n\n{message}"),
    )
    signal_metadata_blocks.append(Divider())
    return Message(blocks=signal_metadata_blocks).build()["blocks"]


def create_genai_signal_analysis_message(
    case: Case,
    db_session: Session,
) -> Tuple[str | dict[str, str], list[Block]]:
    """
    Generates a GenAI signal analysis message for a given case.

    This function generates a GenAI signal analysis message for a specific case by creating metadata blocks
    for the message and attempting to generate a case signal summary using the AI service.

    Args:
        case (Case): The case object for which to create the GenAI signal analysis message.
        db_session (Session): The database session to use for querying and generating the case signal summary.

    Returns:
        Tuple[str | dict[str, str], list[Block]]: A tuple containing the GenAI analysis message (either as a string or a dictionary)
        and the updated list of signal metadata blocks with the GenAI analysis section appended.
    """
    signal_metadata_blocks = []
    try:
        summary = ai_service.generate_case_signal_summary(case, db_session)
    except GenAIException:
        summary = (
            "We encountered an error while generating the GenAI analysis summary for this case."
        )
    return summary, create_genai_signal_message_metadata_blocks(signal_metadata_blocks, summary)


def create_signal_engagement_message(
    case: Case,
    channel_id: str,
    engagement: SignalEngagement | None,
    signal_instance: SignalInstance | None,
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
        signal_instance_id=str(signal_instance.id) if signal_instance else "",
        engagement_id=engagement.id if engagement else 0,
        user=user_email,
    ).json()

    username, _ = user_email.split("@")
    blocks = [
        Section(
            text=f"{engagement.message if engagement and engagement.message else 'No context provided for this alert.'}"
        ),
    ]

    if engagement_status == SignalEngagementStatus.new:
        blocks.extend(
            [
                Section(
                    text="Can you please confirm this was you and whether the behavior was expected?"
                ),
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
                Section(
                    text=f":warning: @{username} denied the behavior as expected. Please investigate the case and escalate to incident if necessary."
                ),
            ]
        )

    return Message(blocks=blocks).build()["blocks"]


def create_manual_engagement_message(
    case: Case,
    channel_id: str,
    user_email: str,
    engagement_status: SignalEngagementStatus = SignalEngagementStatus.new,
    user_id: str = "",
    engagement: str = "",
    thread_ts: str = None,
) -> list[Block]:
    """
    Generate a list of blocks for a manual engagement message.

    Args:
        case (Case): The case object related to the engagement.
        channel_id (str): The ID of the Slack channel where the message will be sent.
        engagement_message (str): The engagement text.
        user_email (str): The email of the user being engaged.

    Returns:
        list[Block]: A list of blocks representing the message structure for the engagement message.
    """
    button_metadata = EngagementMetadata(
        id=case.id,
        type=CaseSubjects.case,
        organization_slug=case.project.organization.slug,
        project_id=case.project.id,
        channel_id=channel_id,
        signal_instance_id="",
        engagement_id=0,
        user=user_email,
        thread_id=thread_ts,
    ).json()

    username, _ = user_email.split("@")
    if engagement:
        blocks = [
            Section(text=f"<@{user_id}>: {engagement}"),
        ]
    else:
        blocks = []

    if engagement_status == SignalEngagementStatus.new:
        blocks.extend(
            [
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
                Section(
                    text=f":warning: @{username} denied the behavior as expected. Please investigate the case and escalate to incident if necessary."
                ),
            ]
        )

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
