from collections import defaultdict
from typing import NamedTuple


from blockkit import (
    Actions,
    Button,
    Context,
    Message,
    Section,
    Divider,
)
from blockkit.surfaces import Block
from sqlalchemy.orm import Session

from dispatch.config import DISPATCH_UI_URL
from dispatch.case.enums import CaseStatus
from dispatch.case.models import Case
from dispatch.entity.models import Entity
from dispatch.entity_type.models import EntityType
from dispatch.entity import service as entity_service
from dispatch.messaging.strings import CASE_STATUS_DESCRIPTIONS, CASE_VISIBILITY_DESCRIPTIONS
from dispatch.plugins.dispatch_slack.models import (
    CaseSubjects,
    EngagementMetadata,
    SubjectMetadata,
    SignalSubjects,
)
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseNotificationActions,
    SignalNotificationActions,
    SignalEngagementActions,
)
from dispatch.signal.models import (
    Signal,
    SignalEngagement,
    SignalInstance,
    assoc_signal_instance_entities,
)
from dispatch.signal.enums import SignalEngagementStatus


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
    priority_color = map_priority_color(color=case.case_priority.color)

    fields = [
        f"*Assignee* \n {case.assignee.individual.email}",
        f"*Status* \n {case.status}",
        f"*Type* \n {case.case_type.name}",
        f"*Priority* \n {priority_color} {case.case_priority.name}",
    ]

    if case.signal_instances:
        if variant := case.signal_instances[0].signal.variant:
            fields.append(f"*Variant* \n {variant}")

    blocks = [
        Context(elements=[f"* {case.name} - Case Details*"]),
        Section(
            text=f"*Title* \n {case.title}.",
            accessory=Button(
                text="Open in Dispatch",
                action_id="button-link",
                url=f"{DISPATCH_UI_URL}/{case.project.organization.slug}/cases/{case.name}",
            ),
        ),
        Section(text=f"*Description* \n {case.description}"),
        Section(fields=fields),
    ]

    button_metadata = SubjectMetadata(
        type=CaseSubjects.case,
        organization_slug=case.project.organization.slug,
        id=case.id,
        project_id=case.project.id,
        channel_id=channel_id,
    ).json()

    if case.status == CaseStatus.escalated:
        blocks.extend(
            [
                Actions(
                    elements=[
                        Button(
                            text="Join Incident",
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
                Section(text=f"*Resolution description* \n {case.resolution}"),
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
                text="Resolve",
                action_id=CaseNotificationActions.resolve,
                style="primary",
                value=button_metadata,
            ),
            Button(
                text="Edit",
                action_id=CaseNotificationActions.edit,
                style="primary",
                value=button_metadata,
            ),
            Button(
                text="Escalate",
                action_id=CaseNotificationActions.escalate,
                style="danger",
                value=button_metadata,
            ),
        ]
        if case.status == CaseStatus.new:
            action_buttons.insert(
                0,
                Button(
                    text="Triage",
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
    """Creates the signal instance message."""

    signal_instances_query = (
        db_session.query(SignalInstance, Signal)
        .join(Signal)
        .with_entities(SignalInstance.id, Signal)
        .filter(SignalInstance.case_id == case_id)
        .order_by(SignalInstance.created_at)
    )

    (first_instance_id, first_instance_signal) = signal_instances_query.first()
    num_of_instances = signal_instances_query.count()

    organization_slug = first_instance_signal.project.organization.slug
    project_id = first_instance_signal.project.id
    button_metadata = SubjectMetadata(
        type=SignalSubjects.signal_instance,
        organization_slug=organization_slug,
        id=str(first_instance_id),
        project_id=project_id,
        channel_id=channel_id,
    ).json()

    # Define the initial elements with "Raw Data" and "Snooze" buttons
    elements = [
        Button(
            text="Snooze",
            action_id=SignalNotificationActions.snooze,
            value=button_metadata,
        ),
    ]

    # Check if `first_instance_signal.external_url` is not empty
    if first_instance_signal.external_url:
        # If `first_instance_signal.external_url` is not empty, add the "Response Plan" button
        elements.append(
            Button(
                text="Response Plan",
                action_id="button-link",
                url=first_instance_signal.external_url,
            )
        )

    # Create the Actions block with the elements
    signal_metadata_blocks = [
        Actions(elements=elements),
        Section(text="*Alerts*"),
        Divider(),
        Section(text=f"{num_of_instances} alerts observed in this case."),
        Section(text="\n*Entities*"),
        Divider(),
    ]

    entities_query = (
        db_session.query(Entity.id, Entity.value, EntityType.name)
        .join(EntityType, Entity.entity_type_id == EntityType.id)
        .join(
            assoc_signal_instance_entities, assoc_signal_instance_entities.c.entity_id == Entity.id
        )
        .join(
            SignalInstance, assoc_signal_instance_entities.c.signal_instance_id == SignalInstance.id
        )
        .filter(SignalInstance.case_id == case_id)
    )

    has_entities = db_session.query(entities_query.exists()).scalar()
    if not has_entities:
        signal_metadata_blocks.append(
            Section(
                text="No entities found.",
            ),
        )
        return Message(blocks=signal_metadata_blocks).build()["blocks"]

    entity_groups = defaultdict(list)
    processed_entities = set()

    for entity_id, entity_value, entity_type_name in entities_query:
        if entity_value not in processed_entities:
            processed_entities.add(entity_value)
            # Fetch the count of related cases with entities in the past 14 days
            entity_case_counts = entity_service.get_case_count_with_entity(
                db_session=db_session, entity_id=entity_id, days_back=14
            )
            entity_groups[entity_type_name].append(
                EntityGroup(
                    value=entity_value,
                    related_case_count=entity_case_counts,
                )
            )

    for k, v in entity_groups.items():
        if v:
            entity_group = v[0]
            case_message = (
                "First time this entity has been seen in a case."
                if entity_group.related_case_count == 1  # the current case counts as 1
                else f"Seen in *{entity_group.related_case_count}* other case(s)."
            )

            # Threaded messages do not overflow text fields, so we hack together the same UI with spaces
            signal_metadata_blocks.append(
                Context(
                    elements=[f"*{k}*\n`{', '.join(item.value for item in v)}`\n\n{case_message}"]
                ),
            )
        signal_metadata_blocks.append(Divider())

    signal_metadata_blocks.append(
        Context(elements=["Correlation is based on two weeks of signal data."]),
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
        Context(elements=[f"Engaged {user_email} associated with {signal_instance.signal.name}"]),
        Section(text=f"Hi @{username}, the security team could use your help with this case."),
        Section(
            text=f"*Additional Context*\n\n {engagement.message if engagement.message else 'None provided for this signal.'}"
        ),
        Divider(),
    ]

    if engagement_status == SignalEngagementStatus.new:
        blocks.extend(
            [
                Section(text="Please confirm this is you and the behavior is expected."),
                Actions(
                    elements=[
                        Button(
                            text="Approve",
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
                Section(text=":white_check_mark: This engagement confirmation has been approved."),
            ]
        )
    else:
        blocks.extend(
            [
                Section(text=":warning: This engagement confirmation has been denied."),
            ]
        )

    return Message(blocks=blocks).build()["blocks"]


def create_welcome_ephemeral_message_to_participant(case: Case) -> list[Block]:
    blocks = [
        Section(
            text="You've been added to this case, because we think you may be able to help resolve it. Please review the case details below and reach out to the case assignee if you have any questions.",
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
