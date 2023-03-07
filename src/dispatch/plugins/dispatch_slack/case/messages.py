from typing import List
from blockkit import Actions, Button, Context, Message, Section, Divider, Overflow, PlainOption

from dispatch.config import DISPATCH_UI_URL
from dispatch.case.enums import CaseStatus
from dispatch.case.models import Case
from dispatch.plugins.dispatch_slack.models import SubjectMetadata
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseNotificationActions,
    SignalNotificationActions,
)
from collections import defaultdict


def create_case_message(case: Case, channel_id: str):
    blocks = [
        Context(elements=["*Case Details*"]),
        Section(
            text=f"*Title* \n {case.title}.",
            accessory=Button(
                text="View",
                action_id="button-link",
                url=f"{DISPATCH_UI_URL}/{case.project.organization.slug}/cases/{case.name}",
            ),
        ),
        Section(
            text=f"*Description* \n {case.description} \n \n Additional information is available in the <{case.case_document.weblink}|case document>."
        ),
        Section(
            fields=[
                f"*Assignee* \n {case.assignee.individual.email}",
                f"*Status* \n {case.status}",
                f"*Severity* \n {case.case_severity.name}",
                f"*Type* \n {case.case_type.name}",
                f"*Priority* \n {case.case_priority.name}",
            ]
        ),
    ]

    button_metadata = SubjectMetadata(
        type="case",
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
                        Overflow(
                            options=[
                                PlainOption(
                                    text="Storage",
                                    url=case.storage.weblink,
                                    value="option-1",
                                ),
                                PlainOption(
                                    text="Document",
                                    url=case.case_document.weblink,
                                    value="option-2",
                                ),
                            ],
                            action_id="button-link",
                        ),
                    ]
                )
            ]
        )

    return Message(blocks=blocks).build()["blocks"]


def create_signal_messages(case: Case, channel_id: str) -> List[Message]:
    """Creates the signal instance message."""
    messages = []

    for instance in case.signal_instances:
        button_metadata = SubjectMetadata(
            type="signalInstance",
            organization_slug=case.project.organization.slug,
            id=str(instance.id),
            project_id=case.project.id,
            channel_id=channel_id,
        ).json()

        signal_metadata_blocks = [
            Section(
                text=f"*Signal Entities* - {instance.id}",
                accessory=Button(
                    text="View Raw",
                    action_id=SignalNotificationActions.view,
                    value=button_metadata,
                ),
            )
        ]

        # group entities by entity type
        entity_groups = defaultdict(list)
        for e in instance.entities:
            entity_groups[e.entity_type.name].append(e.value)

        for k, v in entity_groups.items():
            if v:
                signal_metadata_blocks.append(Section(text=f"*{k}*", fields=v))
            signal_metadata_blocks.append(Divider())

        messages.append(Message(blocks=signal_metadata_blocks[:50]).build()["blocks"])
    return messages
