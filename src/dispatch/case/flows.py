import logging
from datetime import datetime

from sqlalchemy.orm import Session

from dispatch.case import service as case_service
from dispatch.case.messaging import send_case_welcome_participant_message
from dispatch.case.models import CaseRead
from dispatch.conversation import flows as conversation_flows
from dispatch.decorators import background_task
from dispatch.document import flows as document_flows
from dispatch.email_templates import service as email_template_service
from dispatch.email_templates.enums import EmailTemplateTypes
from dispatch.enums import DocumentResourceTypes, EventType, Visibility
from dispatch.event import service as event_service
from dispatch.group import flows as group_flows
from dispatch.group.enums import GroupAction, GroupType
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.messaging import send_participant_announcement_message
from dispatch.incident.models import Incident, IncidentCreate
from dispatch.incident.priority.models import IncidentPriority
from dispatch.incident.type.models import IncidentType
from dispatch.individual import service as individual_service
from dispatch.individual.models import IndividualContactRead
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.participant import flows as participant_flows
from dispatch.participant import service as participant_service
from dispatch.participant.models import ParticipantUpdate
from dispatch.participant_role import flows as role_flow
from dispatch.participant_role.models import ParticipantRole, ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.service import service as service_service
from dispatch.storage import flows as storage_flows
from dispatch.storage.enums import StorageAction
from dispatch.ticket import flows as ticket_flows

from .enums import CaseResolutionReason, CaseStatus
from .messaging import (
    send_case_created_notifications,
    send_case_rating_feedback_message,
    send_case_update_notifications,
    send_event_paging_message,
    send_event_update_prompt_reminder,
)
from .models import Case
from .service import get

log = logging.getLogger(__name__)


def get_case_participants_flow(case: Case, db_session: Session):
    """Get additional case participants based on priority, type and description."""
    individual_contacts = []
    team_contacts = []

    if case.visibility == Visibility.open:
        plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=case.project.id, plugin_type="participant"
        )
        if plugin:
            individual_contacts, team_contacts = plugin.instance.get(
                class_instance=case,
                project_id=case.project.id,
                db_session=db_session,
            )

            event_service.log_case_event(
                db_session=db_session,
                source=plugin.plugin.title,
                description="Case participants resolved",
                case_id=case.id,
            )

    return individual_contacts, team_contacts


@background_task
def case_add_or_reactivate_participant_flow(
    user_email: str,
    case_id: int,
    participant_role: ParticipantRoleType = ParticipantRoleType.observer,
    service_id: int = 0,
    add_to_conversation: bool = True,
    event: dict = None,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the case add or reactive participant flow."""
    case = case_service.get(db_session=db_session, case_id=case_id)

    if service_id:
        # we need to ensure that we don't add another member of a service if one
        # already exists (e.g. overlapping oncalls, we assume they will hand-off if necessary)
        participant = participant_service.get_by_case_id_and_service_id(
            case_id=case_id, service_id=service_id, db_session=db_session
        )

        if participant:
            log.debug("Skipping resolved participant. Oncall service member already engaged.")
            return

    participant = participant_service.get_by_case_id_and_email(
        db_session=db_session, case_id=case.id, email=user_email
    )
    if participant:
        if participant.active_roles:
            return participant

        if case.status != CaseStatus.closed:
            # we reactivate the participant
            participant_flows.reactivate_participant(
                user_email, case, db_session, service_id=service_id
            )
    else:
        # we add the participant to the case
        participant = participant_flows.add_participant(
            user_email, case, db_session, service_id=service_id, roles=[participant_role]
        )
    if case.tactical_group:
        # we add the participant to the tactical group
        group_flows.update_group(
            subject=case,
            group=case.tactical_group,
            group_action=GroupAction.add_member,
            group_member=participant.individual.email,
            db_session=db_session,
        )

    if case.status != CaseStatus.closed:
        # we add the participant to the conversation
        if add_to_conversation:
            conversation_flows.add_case_participants(
                case, [participant.individual.email], db_session
            )

            # check to see if there is an override welcome message template
            welcome_template = email_template_service.get_by_type(
                db_session=db_session,
                project_id=case.project_id,
                email_template_type=EmailTemplateTypes.case_welcome,
            )

            send_case_welcome_participant_message(
                participant_email=user_email,
                case=case,
                db_session=db_session,
                welcome_template=welcome_template,
            )

    return participant


@background_task
def case_remove_participant_flow(
    user_email: str,
    case_id: int,
    db_session: Session,
):
    """Runs the remove participant flow."""
    case = case_service.get(db_session=db_session, case_id=case_id)

    if not case:
        log.warn(
            f"Unable to remove participant from case with id {case_id}. A case with this id does not exist."
        )
        return

    # we remove the participant from the incident
    participant_flows.remove_case_participant(
        user_email=user_email,
        case=case,
        db_session=db_session,
    )

    # we remove the participant from the tactical group
    group_flows.update_group(
        subject=case,
        group=case.tactical_group,
        group_action=GroupAction.remove_member,
        group_member=user_email,
        db_session=db_session,
    )

    # we also try to remove the user from the Slack conversation
    try:
        slack_conversation_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=case.project.id, plugin_type="conversation"
        )

        if not slack_conversation_plugin:
            log.warning(f"{user_email} not updated. No conversation plugin enabled.")
            return

        if not case.conversation:
            log.warning("No conversation enabled for this case.")
            return

        slack_conversation_plugin.instance.remove_user(
            conversation_id=case.conversation.channel_id,
            user_email=user_email
        )

        event_service.log_case_event(
                db_session=db_session,
                source=slack_conversation_plugin.plugin.title,
                description=f"{user_email} removed from conversation (channel ID: {case.conversation.channel_id})",
                case_id=case.id,
                type=EventType.participant_updated,
        )

        log.info(f"Removed {user_email} from conversation in channel {case.conversation.channel_id}")

    except Exception as e:
        log.exception(f"Failed to remove user from Slack conversation: {e}")


def update_conversation(case: Case, db_session: Session) -> None:
    """Updates external communication conversation."""

    # if no case conversation or case has dedicated channel, there's no thread to update
    if case.conversation is None or case.conversation.thread_id is None:
        return

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    plugin.instance.update_thread(
        case=case, conversation_id=case.conversation.channel_id, ts=case.conversation.thread_id
    )

    event_service.log_case_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Case conversation updated.",
        case_id=case.id,
    )


def case_auto_close_flow(case: Case, db_session: Session):
    "Runs the case auto close flow."
    # we mark the case as closed
    case.resolution = "Auto closed via case type auto close configuration."
    case.resolution_reason = CaseResolutionReason.user_acknowledged
    case.status = CaseStatus.closed
    db_session.add(case)
    db_session.commit()

    # we transition the case from the new to the closed state
    case_triage_status_flow(
        case=case,
        db_session=db_session,
    )
    case_closed_status_flow(
        case=case,
        db_session=db_session,
    )

    if case.conversation and case.has_thread:
        # we update the case conversation
        update_conversation(case=case, db_session=db_session)


def case_new_create_flow(
    *,
    case_id: int,
    organization_slug: str | None = None,
    conversation_target: str | None = None,
    service_id: int | None = None,
    db_session: Session,
    create_all_resources: bool = True,
):
    """Runs the case new creation flow."""
    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    # we create the ticket
    ticket_flows.create_case_ticket(case=case, db_session=db_session)

    # we resolve participants
    individual_participants, team_participants = get_case_participants_flow(
        case=case, db_session=db_session
    )

    # NOTE: we create all external resources for a Case unless it's
    # created from a Signal, as it gets expensive when we have lots of them.
    case_create_resources_flow(
        db_session=db_session,
        case_id=case.id,
        individual_participants=individual_participants,
        team_participants=team_participants,
        conversation_target=conversation_target or "",
        create_all_resources=create_all_resources,
    )

    db_session.add(case)
    db_session.commit()

    if case.dedicated_channel:
        send_case_created_notifications(case, db_session)

    if case.case_priority.page_assignee:
        if not service_id:
            if case.case_type.oncall_service:
                service_id = case.case_type.oncall_service.external_id
            else:
                log.warning(
                    "Case assignee not paged. No relationship between case type and an oncall service."
                )
                return case

        oncall_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=case.project.id, plugin_type="oncall"
        )
        if oncall_plugin:
            oncall_plugin.instance.page(
                service_id=service_id,
                incident_name=case.name,
                incident_title=case.title,
                incident_description=case.description,
            )
        else:
            log.warning("Case assignee not paged. No plugin of type oncall enabled.")
            return case
    elif case.event:
        # no one has been paged, inform the channel that they can
        # engage the oncall if the priority changes
        oncall_name = "the relevant team"

        try:
            if case.case_type and case.case_type.oncall_service:
                oncall_service = service_service.get_by_external_id(
                    db_session=db_session,
                    external_id=case.case_type.oncall_service.external_id,
                )
                oncall_name = oncall_service.name
        except Exception as e:
            log.error(
                f"Failed to get oncall service: {e}. Falling back to default oncall_name string."
            )

        # send a message to the channel to inform them that they can engage the oncall
        send_event_paging_message(case, db_session, oncall_name)

        # send ephemeral message to assignee to update the security event
        send_event_update_prompt_reminder(case, db_session)

    if case and case.case_type.auto_close:
        # we transition the case to the closed state if its case type has auto close enabled
        case_auto_close_flow(case=case, db_session=db_session)

    if case.assignee and case.assignee.individual:
        group_flows.update_group(
            subject=case,
            group=case.tactical_group,
            group_action=GroupAction.add_member,
            group_member=case.assignee.individual.email,
            db_session=db_session,
        )

    if case.reporter and case.reporter.individual:
        group_flows.update_group(
            subject=case,
            group=case.tactical_group,
            group_action=GroupAction.add_member,
            group_member=case.reporter.individual.email,
            db_session=db_session,
        )

    return case


@background_task
def case_triage_create_flow(*, case_id: int, organization_slug: OrganizationSlug, db_session=None):
    """Runs the case triage creation flow."""
    # we run the case new creation flow
    case_new_create_flow(
        case_id=case_id, organization_slug=organization_slug, db_session=db_session
    )

    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    # we transition the case to the triage state
    case_triage_status_flow(case=case, db_session=db_session)


@background_task
def case_stable_create_flow(*, case_id: int, organization_slug: OrganizationSlug, db_session=None):
    """Runs the case stable create flow."""
    # we run the case new creation flow
    case_new_create_flow(
        case_id=case_id, organization_slug=organization_slug, db_session=db_session
    )

    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    # we transition the case to the triage state
    case_triage_status_flow(case=case, db_session=db_session)

    case_stable_status_flow(case=case, db_session=db_session)


@background_task
def case_escalated_create_flow(
    *, case_id: int, organization_slug: OrganizationSlug, db_session=None
):
    """Runs the case escalated create flow."""
    # we run the case new creation flow
    case_new_create_flow(
        case_id=case_id, organization_slug=organization_slug, db_session=db_session
    )

    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    # we transition the case to the triage state
    case_triage_status_flow(case=case, db_session=db_session)

    # then to the stable state
    case_stable_status_flow(case=case, db_session=db_session)

    case_escalated_status_flow(
        case=case,
        organization_slug=organization_slug,
        db_session=db_session,
    )


@background_task
def case_closed_create_flow(*, case_id: int, organization_slug: OrganizationSlug, db_session=None):
    """Runs the case closed creation flow."""
    # we run the case new creation flow
    case_new_create_flow(
        case_id=case_id, organization_slug=organization_slug, db_session=db_session
    )

    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    # we transition the case to the triage state
    case_triage_status_flow(case=case, db_session=db_session)

    # we transition the case to the closed state
    case_closed_status_flow(case=case, db_session=db_session)


def case_details_changed(case: Case, previous_case: CaseRead) -> bool:
    """Checks if the case details have changed."""
    return (
        case.case_type.name != previous_case.case_type.name
        or case.case_severity.name != previous_case.case_severity.name
        or case.case_priority.name != previous_case.case_priority.name
        or case.status != previous_case.status
    )


@background_task
def case_update_flow(
    *,
    case_id: int,
    previous_case: CaseRead,
    reporter_email: str | None,
    assignee_email: str | None,
    organization_slug: OrganizationSlug,
    db_session=None,
):
    """Runs the case update flow."""
    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    if not case:
        log.warning(f"Case with id {case_id} not found.")
        return

    if reporter_email and case.reporter and reporter_email != case.reporter.individual.email:
        # we run the case assign role flow for the reporter if it changed
        case_assign_role_flow(
            case_id=case.id,
            participant_email=reporter_email,
            participant_role=ParticipantRoleType.reporter,
            db_session=db_session,
        )

    if assignee_email and case.assignee and assignee_email != case.assignee.individual.email:
        # we run the case assign role flow for the assignee if it changed
        case_assign_role_flow(
            case_id=case.id,
            participant_email=assignee_email,
            participant_role=ParticipantRoleType.assignee,
            db_session=db_session,
        )

    # we run the transition flow based on the current and previous status of the case
    case_status_transition_flow_dispatcher(
        case=case,
        current_status=case.status,
        previous_status=previous_case.status,
        organization_slug=organization_slug,
        db_session=db_session,
    )

    # we update the ticket
    ticket_flows.update_case_ticket(case=case, db_session=db_session)

    if case.status in [CaseStatus.escalated, CaseStatus.closed] and case.case_document:
        # we update the document
        document_flows.update_document(
            document=case.case_document, project_id=case.project.id, db_session=db_session
        )

    if case.tactical_group:
        # we update the tactical group
        if reporter_email and case.reporter and reporter_email != case.reporter.individual.email:
            group_flows.update_group(
                subject=case,
                group=case.tactical_group,
                group_action=GroupAction.add_member,
                group_member=reporter_email,
                db_session=db_session,
            )
        if assignee_email and case.assignee and assignee_email != case.assignee.individual.email:
            group_flows.update_group(
                subject=case,
                group=case.tactical_group,
                group_action=GroupAction.add_member,
                group_member=assignee_email,
                db_session=db_session,
            )

    if case.conversation and case.has_thread:
        # we send the case updated notification
        update_conversation(case, db_session)

    if case.has_channel and not case.has_thread and case.status not in [CaseStatus.escalated, CaseStatus.closed]:
        # determine if case channel topic needs to be updated
        if case_details_changed(case, previous_case):
            conversation_flows.set_conversation_topic(case, db_session)

    # we send the case update notifications
    if case.dedicated_channel:
        send_case_update_notifications(case, previous_case, db_session)


def case_delete_flow(case: Case, db_session: Session):
    """Runs the case delete flow."""
    # we delete the external ticket
    if case.ticket:
        ticket_flows.delete_ticket(
            ticket=case.ticket, project_id=case.project.id, db_session=db_session
        )

    # we delete the external groups
    if case.groups:
        for group in case.groups:
            group_flows.delete_group(group=group, project_id=case.project.id, db_session=db_session)

    # we delete the external storage
    if case.storage:
        storage_flows.delete_storage(
            storage=case.storage, project_id=case.project.id, db_session=db_session
        )


def case_new_status_flow(case: Case, db_session=None):
    """Runs the case new transition flow."""
    pass


def case_triage_status_flow(case: Case, db_session=None):
    """Runs the case triage transition flow."""
    # we set the triage_at time during transitions if not already set
    if not case.triage_at:
        case.triage_at = datetime.utcnow()
        db_session.add(case)
        db_session.commit()


def case_escalated_status_flow(
    case: Case,
    organization_slug: OrganizationSlug,
    db_session: Session,
    title: str | None,
    incident_priority: IncidentPriority | None,
    incident_type: IncidentType | None,
    incident_description: str | None,
):
    """Runs the case escalated status flow."""
    # we set the escalated at time
    case.escalated_at = datetime.utcnow()
    db_session.add(case)
    db_session.commit()

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Case escalated",
        case_id=case.id,
    )

    case_to_incident_escalate_flow(
        case=case,
        organization_slug=organization_slug,
        db_session=db_session,
        title=title,
        incident_priority=incident_priority,
        incident_type=incident_type,
        incident_description=incident_description,
    )


def case_stable_status_flow(case: Case, db_session=None):
    """Runs the case stable status flow."""
    # we set the stable at time
    case.stable_at = datetime.utcnow()
    db_session.add(case)
    db_session.commit()

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Case marked as stable",
        case_id=case.id,
    )


def case_closed_status_flow(case: Case, db_session=None):
    """Runs the case closed transition flow."""
    # we set the closed_at time
    case.closed_at = datetime.utcnow()
    db_session.add(case)
    db_session.commit()

    # Archive the conversation if there is a dedicated channel
    if case.dedicated_channel:
        conversation_flows.archive_conversation(subject=case, db_session=db_session)

    # Check if the case visibility is open
    if case.visibility != Visibility.open:
        return

    # Get the active storage plugin for the case's project
    storage_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="storage"
    )

    if not storage_plugin:
        return

    # we update the ticket
    ticket_flows.update_case_ticket(case=case, db_session=db_session)

    # Open document access if configured
    if storage_plugin.configuration.open_on_close:
        for document in case.documents:
            document_flows.open_document_access(document=document, db_session=db_session)

    # Mark documents as read-only if configured
    if storage_plugin.configuration.read_only:
        for document in case.documents:
            document_flows.mark_document_as_readonly(document=document, db_session=db_session)

    if case.dedicated_channel:
        # we send a direct message to all participants asking them
        # to rate and provide feedback about the case
        send_case_rating_feedback_message(case, db_session)


def reactivate_case_participants(case: Case, db_session: Session):
    """Reactivates all case participants."""
    for participant in case.participants:
        try:
            case_add_or_reactivate_participant_flow(
                participant.individual.email, case.id, db_session=db_session
            )
        except Exception as e:
            # don't fail to reactivate all participants if one fails
            event_service.log_case_event(
                db_session=db_session,
                source="Dispatch Core App",
                description=f"Unable to reactivate participant with email {participant.individual.email}",
                case_id=case.id,
                type=EventType.participant_updated,
            )
            log.exception(e)

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Case participants reactivated",
        case_id=case.id,
        type=EventType.participant_updated,
    )


def case_active_status_flow(case: Case, db_session: Session) -> None:
    """Runs the case active flow."""
    # we un-archive the conversation
    if case.dedicated_channel:
        conversation_flows.unarchive_conversation(subject=case, db_session=db_session)
        reactivate_case_participants(case, db_session)


def case_status_transition_flow_dispatcher(
    case: Case,
    current_status: CaseStatus,
    previous_status: CaseStatus,
    organization_slug: OrganizationSlug,
    db_session: Session,
):
    """Runs the correct flows based on the current and previous status of the case."""
    log.info(
        "Transitioning Case status",
        extra={
            "case_id": case.id,
            "previous_status": previous_status,
            "current_status": current_status,
        },
    )
    match (previous_status, current_status):
        case (CaseStatus.closed, CaseStatus.new):
            # Closed -> New
            case_active_status_flow(case, db_session)

        case (_, CaseStatus.new):
            # Any -> New
            pass

        case (CaseStatus.new, CaseStatus.triage):
            # New -> Triage
            case_triage_status_flow(
                case=case,
                db_session=db_session,
            )

        case (CaseStatus.closed, CaseStatus.triage):
            # Closed -> Triage
            case_active_status_flow(case, db_session)
            case_triage_status_flow(
                case=case,
                db_session=db_session,
            )

        case (_, CaseStatus.triage):
            # Any -> Triage/
            log.warning(
                "Unexpected previous state for Case transition to Triage state.",
                extra={
                    "case_id": case.id,
                    "previous_status": previous_status,
                    "current_status": current_status,
                },
            )

        case (CaseStatus.new, CaseStatus.escalated):
            # New -> Escalated
            case_triage_status_flow(
                case=case,
                db_session=db_session,
            )
            case_escalated_status_flow(
                case=case,
                organization_slug=organization_slug,
                db_session=db_session,
            )

        case (CaseStatus.triage, CaseStatus.escalated):
            # Triage -> Escalated
            case_escalated_status_flow(
                case=case,
                organization_slug=organization_slug,
                db_session=db_session,
            )

        case (CaseStatus.closed, CaseStatus.escalated):
            # Closed -> Escalated
            case_active_status_flow(case, db_session)
            case_triage_status_flow(
                case=case,
                db_session=db_session,
            )
            case_escalated_status_flow(
                case=case,
                organization_slug=organization_slug,
                db_session=db_session,
            )

        case (_, CaseStatus.escalated):
            # Any -> Escalated
            pass

        case (CaseStatus.new, CaseStatus.closed):
            # New -> Closed
            case_triage_status_flow(
                case=case,
                db_session=db_session,
            )
            case_closed_status_flow(
                case=case,
                db_session=db_session,
            )

        case (CaseStatus.triage, CaseStatus.closed):
            # Triage -> Closed
            case_closed_status_flow(
                case=case,
                db_session=db_session,
            )

        case (CaseStatus.escalated, CaseStatus.closed):
            # Escalated -> Closed
            case_closed_status_flow(
                case=case,
                db_session=db_session,
            )

        case (CaseStatus.escalated, CaseStatus.stable):
            # Escalated -> Stable
            case_stable_status_flow(
                case=case,
                db_session=db_session,
            )

        case (CaseStatus.triage, CaseStatus.stable):
            # Triage -> Stable
            case_stable_status_flow(
                case=case,
                db_session=db_session,
            )

        case (CaseStatus.new, CaseStatus.stable):
            # New -> Stable
            case_triage_status_flow(
                case=case,
                db_session=db_session,
            )
            case_stable_status_flow(
                case=case,
                db_session=db_session,
            )

        case (CaseStatus.stable, CaseStatus.closed):
            # Stable -> Closed
            case_closed_status_flow(
                case=case,
                db_session=db_session,
            )

        case (CaseStatus.closed, CaseStatus.stable):
            # Closed -> Stable
            case_active_status_flow(case, db_session)
            case_stable_status_flow(
                case=case,
                db_session=db_session,
            )

        case (_, _):
            pass


def send_escalation_messages_for_channel_case(
    case: Case,
    db_session: Session,
    incident: Incident,
):
    from dispatch.plugins.dispatch_slack.incident import messages

    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    if plugin is None:
        log.warning("Case close reminder message not sent. No conversation plugin enabled.")
        return

    plugin.instance.send_message(
        conversation_id=incident.conversation.channel_id,
        blocks=messages.create_incident_channel_escalate_message(),
    )


def map_case_roles_to_incident_roles(
    participant_roles: list[ParticipantRole], incident: Incident, db_session: Session
) -> list[ParticipantRoleType | None]:
    # Map the case role to an incident role
    incident_roles = set()
    for role in participant_roles:
        if role.role == ParticipantRoleType.assignee:
            # If incident commader role already assigned, assign as participant
            if participant_service.get_by_incident_id_and_role(
                db_session=db_session,
                incident_id=incident.id,
                role=ParticipantRoleType.incident_commander,
            ):
                incident_roles.add(ParticipantRoleType.participant)
            else:
                incident_roles.add(ParticipantRoleType.incident_commander)
        else:
            incident_roles.add(role.role)
    return list(incident_roles) or None


def copy_case_events_to_incident(
    case: Case,
    incident: Incident,
    db_session: Session,
):
    """Copies all timeline events from a case to an incident."""
    # Get all events from the case
    case_events = event_service.get_by_case_id(db_session=db_session, case_id=case.id).all()

    if not case_events:
        log.info(f"No events to copy from case {case.id} to incident {incident.id}")
        return

    log.info(f"Copying {len(case_events)} events from case {case.id} to incident {incident.id}")

    for case_event in case_events:
        # Create a new event for the incident with the same data
        copied_source = f"{case_event.source} (copied from {case.name})"
        event_service.log_incident_event(
            db_session=db_session,
            source=copied_source,
            description=case_event.description,
            incident_id=incident.id,
            individual_id=case_event.individual_id,
            started_at=case_event.started_at,
            ended_at=case_event.ended_at,
            details=case_event.details,
            type=case_event.type,
            owner=case_event.owner,
            pinned=case_event.pinned,
        )

    log.info(
        f"Successfully copied {len(case_events)} events from case {case.id} to incident {incident.id}"
    )


def common_escalate_flow(
    case: Case,
    incident: Incident,
    organization_slug: OrganizationSlug,
    db_session: Session,
):
    # This is a channel based Case, so we reuse the case conversation for the incident
    if case.has_channel:
        incident.conversation = case.conversation
        db_session.add(incident)
        db_session.commit()

    # we run the incident create flow in a background task
    incident = incident_flows.incident_create_flow(
        incident_id=incident.id,
        organization_slug=organization_slug,
        db_session=db_session,
        case_id=case.id,
    )

    # we link the case to the incident
    case.incidents.append(incident)
    db_session.add(case)
    db_session.commit()

    # Copy timeline events from case to incident
    copy_case_events_to_incident(case=case, incident=incident, db_session=db_session)

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description=f"The case has been linked to incident {incident.name} in the {incident.project.name} project",
        case_id=case.id,
    )

    # we add the case participants to the incident
    for participant in case.participants:
        # check to see if already a participant in the incident
        incident_participant = participant_service.get_by_incident_id_and_email(
            db_session=db_session, incident_id=incident.id, email=participant.individual.email
        )

        if not incident_participant:
            log.info(
                f"Adding participant {participant.individual.email} from Case {case.id} to Incident {incident.id}"
            )
            # Get the roles for this participant
            incident_roles = map_case_roles_to_incident_roles(
                participant_roles=participant.participant_roles,
                incident=incident,
                db_session=db_session,
            )

            participant_flows.add_participant(
                user_email=participant.individual.email,
                subject=incident,
                db_session=db_session,
                roles=incident_roles,
            )

            # We add the participants to the conversation
            conversation_flows.add_incident_participants_to_conversation(
                db_session=db_session,
                incident=incident,
                participant_emails=[participant.individual.email],
            )

            # Add the participant to the incident tactical group if active
            if participant.active_roles:
                group_flows.update_group(
                    subject=incident,
                    group=incident.tactical_group,
                    group_action=GroupAction.add_member,
                    group_member=participant.individual.email,
                    db_session=db_session,
                )

    if case.has_channel:
        # depends on `incident_create_flow()` (we need incident.name), so we invoke after we call it
        send_escalation_messages_for_channel_case(
            case=case,
            db_session=db_session,
            incident=incident,
        )

    if case.storage and incident.tactical_group:
        storage_members = [incident.tactical_group.email]
        storage_flows.update_storage(
            subject=case,
            storage_action=StorageAction.add_members,
            storage_members=storage_members,
            db_session=db_session,
        )

        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=(
                f"The members of the incident's tactical group {incident.tactical_group.email} "
                f"have been given permission to access the case's storage folder"
            ),
            case_id=case.id,
        )


def case_to_incident_escalate_flow(
    case: Case,
    organization_slug: OrganizationSlug,
    db_session: Session,
    title: str | None,
    incident_priority: IncidentPriority | None,
    incident_type: IncidentType,
    incident_description: str | None,
):
    if case.incidents:
        return

    # use existing reporter or assignee if none
    reporter = (
        ParticipantUpdate(individual=IndividualContactRead(email=case.reporter.individual.email))
        if case.reporter
        else ParticipantUpdate(
            individual=IndividualContactRead(email=case.assignee.individual.email)
        )
    )

    title = title if title else case.title

    description = (
        f"{incident_description if incident_description else case.description}\n\n"
        f"This incident was the result of escalating case {case.name} "
        f"in the {case.project.name} project. Check out the case in the Dispatch Web UI for additional context."
    )

    incident_priority = incident_priority if incident_priority else case.case_priority

    incident_in = IncidentCreate(
        title=title,
        description=description,
        status=IncidentStatus.active,
        incident_type=incident_type,
        incident_priority=incident_priority,
        project=case.project,
        reporter=reporter,
    )
    incident = incident_service.create(db_session=db_session, incident_in=incident_in)

    common_escalate_flow(
        case=case,
        incident=incident,
        organization_slug=organization_slug,
        db_session=db_session,
    )


@background_task
def case_to_incident_endpoint_escalate_flow(
    case_id: PrimaryKey,
    incident_id: PrimaryKey,
    organization_slug: OrganizationSlug,
    db_session: Session = None,
):
    case = get(case_id=case_id, db_session=db_session)

    case_triage_status_flow(case=case, db_session=db_session)
    case.escalated_at = datetime.utcnow()
    case.status = CaseStatus.escalated
    db_session.commit()

    incident = incident_service.get(db_session=db_session, incident_id=incident_id)

    common_escalate_flow(
        case=case,
        incident=incident,
        organization_slug=organization_slug,
        db_session=db_session,
    )


def case_assign_role_flow(
    case_id: int,
    participant_email: str,
    participant_role: str,
    db_session: Session,
):
    """Runs the case participant role assignment flow."""
    # we get the case
    case = get(case_id=case_id, db_session=db_session)

    # we add the participant to the incident if they're not a member already
    case_add_or_reactivate_participant_flow(participant_email, case.id, db_session=db_session)

    # we run the assign role flow
    result = role_flow.assign_role_flow(case, participant_email, participant_role, db_session)

    if result in ["assignee_has_role", "role_not_assigned"]:
        return

    # we stop here if this is not a dedicated channel case
    if not case.dedicated_channel:
        return

    if case.status != CaseStatus.closed and participant_role == ParticipantRoleType.assignee:
        # update the conversation topic
        conversation_flows.set_conversation_topic(case, db_session)


def case_create_conversation_flow(
    db_session: Session,
    case: Case,
    participant_emails: list[str],
    conversation_target: str | None = None,
) -> None:
    """Runs the case conversation creation flow."""

    conversation_flows.create_case_conversation(case, conversation_target, db_session)

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Conversation added to case",
        case_id=case.id,
    )

    for email in participant_emails:
        # we don't rely on on this flow to add folks to the conversation because in this case
        # we want to do it in bulk
        case_add_or_reactivate_participant_flow(
            db_session=db_session,
            user_email=email,
            case_id=case.id,
            add_to_conversation=False,
        )

    # we add the participant to the conversation
    conversation_flows.add_case_participants(
        case=case,
        participant_emails=participant_emails,
        db_session=db_session,
    )


def case_create_resources_flow(
    db_session: Session,
    case_id: int,
    individual_participants: list[str],
    team_participants: list[str],
    conversation_target: str = None,
    create_all_resources: bool = True,
) -> None:
    """Runs the case resource creation flow."""
    case = get(db_session=db_session, case_id=case_id)

    if case.assignee:
        individual_participants.append((case.assignee.individual, None))

    if case.reporter:
        individual_participants.append((case.reporter.individual, None))

    if create_all_resources:
        # we create the tactical group
        direct_participant_emails = [i.email for i, _ in individual_participants]

        indirect_participant_emails = [t.email for t in team_participants]

        if not case.groups:
            group_flows.create_group(
                subject=case,
                group_type=GroupType.tactical,
                group_participants=list(
                    set(direct_participant_emails + indirect_participant_emails)
                ),
                db_session=db_session,
            )

        # we create the storage folder
        storage_members = []
        if case.tactical_group:
            storage_members = [case.tactical_group.email]
        # direct add members if not group exists
        else:
            storage_members = direct_participant_emails

        if not case.storage:
            storage_flows.create_storage(
                subject=case, storage_members=storage_members, db_session=db_session
            )

        # we create the investigation document
        if not case.case_document:
            document_flows.create_document(
                subject=case,
                document_type=DocumentResourceTypes.case,
                document_template=case.case_type.case_template_document,
                db_session=db_session,
            )

        # we update the case document
        document_flows.update_document(
            document=case.case_document, project_id=case.project.id, db_session=db_session
        )

    try:
        # wait until all resources are created before adding suggested participants
        individual_participants = [x.email for x, _ in individual_participants]

        # we create the conversation and add participants to the thread
        case_create_conversation_flow(
            db_session=db_session,
            case=case,
            participant_emails=individual_participants,
            conversation_target=conversation_target,
        )

        # check to see if there is an override welcome message template
        welcome_template = email_template_service.get_by_type(
            db_session=db_session,
            project_id=case.project_id,
            email_template_type=EmailTemplateTypes.case_welcome,
        )

        for user_email in set(individual_participants):
            send_participant_announcement_message(
                db_session=db_session,
                participant_email=user_email,
                subject=case,
            )

            send_case_welcome_participant_message(
                participant_email=user_email,
                case=case,
                db_session=db_session,
                welcome_template=welcome_template,
            )

        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description="Case participants added to conversation.",
            case_id=case.id,
        )
    except Exception as e:
        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Creation of case conversation failed. Reason: {e}",
            case_id=case.id,
        )
        log.exception(e)

    if case.has_channel:
        bookmarks = [
            # resource, title
            (case.case_document, None),
            (case.ticket, "Case Ticket"),
            (case.storage, "Case Storage"),
        ]
        for resource, title in bookmarks:
            conversation_flows.add_conversation_bookmark(
                subject=case,
                resource=resource,
                db_session=db_session,
                title=title,
            )
        conversation_flows.set_conversation_topic(case, db_session)

    # we update the ticket
    ticket_flows.update_case_ticket(case=case, db_session=db_session)


@background_task
def case_engage_oncall_flow(
    user_email: str,
    case_id: int,
    oncall_service_external_id: str,
    page=None,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the case engage oncall flow."""
    # we load the case instance
    case = case_service.get(db_session=db_session, case_id=case_id)

    # we resolve the oncall service
    oncall_service = service_service.get_by_external_id_and_project_id(
        db_session=db_session,
        external_id=oncall_service_external_id,
        project_id=case.project.id,
    )

    # we get the active oncall plugin
    oncall_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="oncall"
    )

    if oncall_plugin:
        if oncall_plugin.plugin.slug != oncall_service.type:
            log.warning(
                f"Unable to engage the oncall. Oncall plugin enabled not of type {oncall_plugin.plugin.slug}."  # noqa
            )
            return None, None
    else:
        log.warning("Unable to engage the oncall. No oncall plugins enabled.")
        return None, None

    oncall_email = oncall_plugin.instance.get(service_id=oncall_service_external_id)

    # we attempt to add the oncall to the case
    oncall_participant_added = case_add_or_reactivate_participant_flow(
        user_email=oncall_email,
        case_id=case.id,
        service_id=oncall_service.id,
        db_session=db_session,
    )

    if not oncall_participant_added:
        # we already have the oncall for the service in the case
        return None, oncall_service

    individual = individual_service.get_by_email_and_project(
        db_session=db_session, email=user_email, project_id=case.project.id
    )

    event_service.log_case_event(
        db_session=db_session,
        source=oncall_plugin.plugin.title,
        description=f"{individual.name} engages oncall service {oncall_service.name}",
        case_id=case.id,
    )

    if page == "Yes":
        # we page the oncall
        oncall_plugin.instance.page(
            service_id=oncall_service_external_id,
            incident_name=case.name,
            incident_title=case.title,
            incident_description=case.description,
            event_type="case",
        )

        event_service.log_case_event(
            db_session=db_session,
            source=oncall_plugin.plugin.title,
            description=f"{oncall_service.name} on-call paged",
            case_id=case.id,
        )

    return oncall_participant_added.individual, oncall_service
