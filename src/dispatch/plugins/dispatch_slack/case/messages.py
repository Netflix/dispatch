from typing import List
from blockkit import Actions, Button, Context, Message, Section, Divider, Overflow, PlainOption

from dispatch.config import DISPATCH_UI_URL
from dispatch.case.enums import CaseStatus
from dispatch.case.models import Case
from dispatch.plugins.dispatch_slack.models import SubjectMetadata
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseNotificationActions,
)
from dispatch.plugins.dispatch_slack.service import chunks


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


def create_signal_messages(case: Case) -> List[Message]:
    """Creates the signal instance message."""
    messages = []
    for instance in case.signal_instances:
        signal_metadata_blocks = [
            Section(
                text="*Signal Details*",
                accessory=Button(
                    text="View",
                    url=f"{DISPATCH_UI_URL}/{case.project.organization.slug}/signals/{instance.id}",
                ),
            ),
        ]
        if instance.raw.get("identity"):
            signal_metadata_blocks.append(Context(elements=["*Identity*"]))

            signal_metadata_blocks.append(
                Section(
                    fields=[
                        f"*{k.strip()}* \n {v.strip()}" for k, v in instance.raw["identity"].items()
                    ]
                )
            )
            signal_metadata_blocks.append(Divider())

        if instance.raw.get("action"):
            signal_metadata_blocks.append(Context(elements=["*Actions*"]))
            for item in instance.raw["action"]:
                signal_metadata_blocks.append(Context(elements=[f"*{item['type']}*"]))
                for chunk in chunks([(k, v) for k, v in item["value"].items()], 10):
                    signal_metadata_blocks.append(
                        Section(fields=[f"*{k.strip()}* \n {v.strip()}" for k, v in chunk]),
                    )
            signal_metadata_blocks.append(Divider())

        if instance.raw.get("origin_location"):
            signal_metadata_blocks.append(Context(elements=["*Origin Location*"]))
            for item in instance.raw["origin_location"]:
                signal_metadata_blocks.append(
                    Section(fields=[f"*{item['type'].strip()}* \n {item['value'].strip()}"]),
                )
            signal_metadata_blocks.append(Divider())

        if instance.raw.get("asset"):
            signal_metadata_blocks.append(Context(elements=["*Assets*"]))
            for item in instance.raw["asset"]:
                signal_metadata_blocks.append(
                    Section(fields=[f"*{item['type'].strip()}* \n {item['id'].strip()}"]),
                )
            signal_metadata_blocks.append(Divider())

        for item in instance.raw.get("additional_metadata", []):
            signal_metadata_blocks.append(Context(elements=[f"*{item['name']}*"]))

            if isinstance(item["value"], dict):
                # sections have a hard limit of 10 fields
                for chunk in chunks([(k, v) for k, v in item["value"].items()], 10):
                    signal_metadata_blocks.append(
                        Section(fields=[f"*{k.strip()}* \n {v.strip()}" for k, v in chunk]),
                    )
            else:
                # remove empty strings
                if item["value"]:
                    signal_metadata_blocks.append(
                        Section(text=str(item["value"]).strip()),
                    )

        # limit the number of total messages
        messages.append(Message(blocks=signal_metadata_blocks[:50]).build()["blocks"])
    return messages
