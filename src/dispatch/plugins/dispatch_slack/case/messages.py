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

from dispatch.auth.models import DispatchUser
from dispatch.config import DISPATCH_UI_URL
from dispatch.case.enums import CaseStatus
from dispatch.case.models import Case
from dispatch.entity.models import Entity
from dispatch.entity_type.models import EntityType
from dispatch.entity import service as entity_service
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


def create_case_message(case: Case, channel_id: str) -> list[Block]:
    fields = [
        f"*Assignee* \n {case.assignee.individual.email}",
        f"*Status* \n {case.status}",
        f"*Severity* \n {case.case_severity.name}",
        f"*Type* \n {case.case_type.name}",
        f"*Priority* \n {case.case_priority.name}",
    ]

    if case.signal_instances:
        fields.append(f"*Variant* \n {case.signal_instances[0].signal.variant}")

    blocks = [
        Context(elements=[f"* {case.name} - Case Details*"]),
        Section(
            text=f"*Title* \n {case.title}.",
            accessory=Button(
                text="View",
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
                Actions(
                    elements=[
                        Button(
                            text="Re-open",
                            action_id=CaseNotificationActions.reopen,
                            style="primary",
                            value=button_metadata,
                        )
                    ]
                )
            ]
        )
    else:
        blocks.extend(
            [
                Actions(
                    elements=[
                        Button(
                            text="Edit",
                            action_id=CaseNotificationActions.edit,
                            style="primary",
                            value=button_metadata,
                        ),
                        Button(
                            text="Resolve",
                            action_id=CaseNotificationActions.resolve,
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
                )
            ]
        )

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

    signal_metadata_blocks = [
        Section(
            text=f"*{first_instance_signal.name}* - {first_instance_signal.variant}",
        ),
        Actions(
            elements=[
                Button(
                    text="Raw Data",
                    action_id=SignalNotificationActions.view,
                    value=button_metadata,
                ),
                Button(
                    text="Snooze",
                    action_id=SignalNotificationActions.snooze,
                    value=button_metadata,
                ),
                Button(
                    text="Response Plan",
                    action_id="button-link",
                    url=first_instance_signal.external_url,
                ),
            ]
        ),
        Section(text=f"Total instances in this case: *{num_of_instances}*\n"),
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
    user: DispatchUser,
    engagement_status: SignalEngagementStatus = SignalEngagementStatus.new,
) -> list[Block]:
    """
    Generate a list of blocks for a signal engagement message.

    Args:
        case (Case): The case object related to the signal instance.
        channel_id (str): The ID of the Slack channel where the message will be sent.
        message (str): Additional context information to include in the message.
        signal_instance (SignalInstance): The signal instance object related to the engagement.
        user (DispatchUser): The DispatchUser being engaged.
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
        user=user.email,
    ).json()

    username, _ = user.email.split("@")
    blocks = [
        Context(elements=[f"Engaged {user.email} associated with {signal_instance.signal.name}"]),
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
