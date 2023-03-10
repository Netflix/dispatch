from collections import defaultdict, namedtuple
from typing import List

from blockkit import Actions, Button, Context, Message, Section, Divider, Overflow, PlainOption
from sqlalchemy.orm import Session

from dispatch.config import DISPATCH_UI_URL
from dispatch.case.enums import CaseStatus
from dispatch.case.models import Case
from dispatch.entity import service as entity_service
from dispatch.plugins.dispatch_slack.models import SubjectMetadata, CaseSubjects, SignalSubjects
from dispatch.plugins.dispatch_slack.case.enums import (
    CaseNotificationActions,
    SignalNotificationActions,
)


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


def create_signal_messages(case: Case, channel_id: str, db_session: Session) -> List[Message]:
    """Creates the signal instance message."""
    messages = []

    for instance in case.signal_instances:
        button_metadata = SubjectMetadata(
            type=SignalSubjects.signal_instance,
            organization_slug=case.project.organization.slug,
            id=str(instance.id),
            project_id=case.project.id,
            channel_id=channel_id,
        ).json()

        signal_metadata_blocks = [
            Section(
                text=f"*{instance.signal.name}* - {instance.signal.variant}",
            ),
            Actions(
                elements=[
                    Button(
                        text="View Raw Data",
                        action_id=SignalNotificationActions.view,
                        value=button_metadata,
                    ),
                    Button(
                        text="Snooze",
                        action_id=SignalNotificationActions.snooze,
                        value=button_metadata,
                    ),
                ]
            ),
            Section(text="*Entities*"),
            Divider(),
        ]

        if not instance.entities:
            signal_metadata_blocks.append(
                Section(
                    text="No entities found.",
                ),
            )
        EntityGroup = namedtuple(
            "EntityGroup", ["value", "related_instance_count", "related_case_count"]
        )
        entity_groups = defaultdict(list)
        for e in instance.entities:
            related_instances = entity_service.get_signal_instances_with_entity(
                db_session=db_session, entity_id=e.id, days_back=14
            )
            related_instance_count = len(related_instances)

            related_cases = entity_service.get_cases_with_entity(
                db_session=db_session, entity_id=e.id, days_back=14
            )
            related_case_count = len(related_cases)
            entity_groups[e.entity_type.name].append(
                EntityGroup(
                    value=e.value,
                    related_instance_count=related_instance_count,
                    related_case_count=related_case_count,
                )
            )
        for k, v in entity_groups.items():
            if v:
                related_instance_count = v[0].related_instance_count
                match related_instance_count:
                    case 0:
                        signal_message = "First time this entity has been seen in a signal."
                    case 1:
                        signal_message = f"Seen in *{related_instance_count}* other signal."
                    case _:
                        signal_message = f"Seen in *{related_instance_count}* other signals."

                related_case_count = v[0].related_case_count
                match related_case_count:
                    case 0:
                        case_message = "First time this entity has been seen in a case."
                    case 1:
                        case_message = f"Seen in *{related_instance_count}* other case."
                    case _:
                        case_message = f"Seen in *{related_instance_count}* other cases."

                # dynamically allocate space for the entity type name and entity type values
                entity_type_name_length = len(k)
                entity_type_value_length = len(", ".join(item.value for item in v))
                entity_type_name_spaces = " " * (55 - entity_type_name_length)
                entity_type_value_spaces = " " * (50 - entity_type_value_length)

                # Threaded messages do not overflow text fields, so we hack together the same UI with spaces
                signal_metadata_blocks.append(
                    Context(
                        elements=[
                            f"*{k}*{entity_type_name_spaces}{signal_message}\n`{', '.join(item.value for item in v)}`{entity_type_value_spaces}{case_message}"
                        ]
                    ),
                )
            signal_metadata_blocks.append(Divider())

        signal_metadata_blocks.append(
            Context(elements=["Correlation is based on two weeks of signal data."]),
        )
        messages.append(Message(blocks=signal_metadata_blocks[:50]).build()["blocks"])
    return messages
