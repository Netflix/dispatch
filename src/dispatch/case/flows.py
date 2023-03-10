import logging
from datetime import datetime
from typing import List

from dispatch.case import service as case_service
from dispatch.case.models import CaseRead
from dispatch.conversation import service as conversation_service
from dispatch.conversation.models import ConversationCreate
from dispatch.database.core import SessionLocal
from dispatch.decorators import background_task
from dispatch.document import flows as document_flows
from dispatch.enums import DocumentResourceTypes, Visibility
from dispatch.event import service as event_service
from dispatch.group import flows as group_flows
from dispatch.group.enums import GroupAction, GroupType
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import IncidentCreate
from dispatch.individual.models import IndividualContactRead
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.participant import service as participant_service
from dispatch.participant import flows as participant_flows
from dispatch.participant_role import flows as role_flow
from dispatch.participant.models import ParticipantUpdate
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.storage import flows as storage_flows
from dispatch.storage.enums import StorageAction
from dispatch.ticket import flows as ticket_flows

from .models import Case, CaseStatus
from .service import get

log = logging.getLogger(__name__)


def get_case_participants(case: Case, db_session: SessionLocal):
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


def add_participants_to_conversation(
    participant_emails: List[str], case: Case, db_session: SessionLocal
):
    """Adds one or more participants to the case conversation."""
    if not case.conversation:
        log.warning(
            "Case participant(s) not added to conversation. No conversation available for this case."
        )
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    if not plugin:
        log.warning(
            "Incident participant(s) not added to conversation. No conversation plugin enabled."
        )
        return

    try:
        plugin.instance.add_to_thread(
            case.conversation.channel_id, case.conversation.thread_id, participant_emails
        )
    except Exception as e:
        event_service.log_case_event(
            db_session=db_session,
            source="Dispatch Core App",
            description=f"Adding participant(s) to case conversation failed. Reason: {e}",
            case_id=case.id,
        )
        log.exception(e)


@background_task
def case_add_or_reactivate_participant_flow(
    user_email: str,
    case_id: int,
    participant_role: ParticipantRoleType = ParticipantRoleType.participant,
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
        # we add the participant to the incident
        participant = participant_flows.add_participant(
            user_email, case, db_session, service_id=service_id, role=participant_role
        )

    # we add the participant to the tactical group
    # add_participant_to_tactical_group(user_email, case, db_session)

    if case.status != CaseStatus.closed:
        # we add the participant to the conversation
        if add_to_conversation:
            add_participants_to_conversation([user_email], case, db_session)

    return participant


def create_conversation(case: Case, db_session: SessionLocal):
    """Create external communication conversation."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    conversation = plugin.instance.create_threaded(
        case=case, conversation_id=case.case_type.conversation_target
    )
    conversation.update({"resource_type": plugin.plugin.slug, "resource_id": conversation["id"]})

    event_service.log_case_event(
        db_session=db_session,
        source=plugin.plugin.title,
        description="Case conversation created",
        case_id=case.id,
    )

    return conversation


def update_conversation(case: Case, db_session: SessionLocal):
    """Updates external communication conversation."""
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


@background_task
def case_new_create_flow(*, case_id: int, organization_slug: OrganizationSlug, db_session=None):
    """Runs the case new creation flow."""
    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    # we create the ticket
    ticket_flows.create_case_ticket(case=case, db_session=db_session)

    individual_participants, team_participants = get_case_participants(
        case=case, db_session=db_session
    )

    # we create the tactical group
    direct_participant_emails = [i.email for i, _ in individual_participants]
    direct_participant_emails.append(case.assignee.individual.email)

    indirect_participant_emails = [t.email for t in team_participants]
    group = group_flows.create_group(
        subject=case,
        group_type=GroupType.tactical,
        group_participants=list(set(direct_participant_emails + indirect_participant_emails)),
        db_session=db_session,
    )

    # we create the storage folder
    storage_members = []
    if group:
        storage_members = [group.email]

    # direct add members if not group exists
    else:
        storage_members = direct_participant_emails

    case.storage = storage_flows.create_storage(
        subject=case, storage_members=storage_members, db_session=db_session
    )

    # we create the investigation document
    document = document_flows.create_document(
        subject=case,
        document_type=DocumentResourceTypes.case,
        document_template=case.case_type.case_template_document,
        db_session=db_session,
    )

    # we update the ticket
    ticket_flows.update_case_ticket(case=case, db_session=db_session)

    # we update the case document
    document_flows.update_document(
        document=document, project_id=case.project.id, db_session=db_session
    )

    if case.case_priority.page_assignee:
        if case.case_type.oncall_service:
            service_id = case.case_type.oncall_service.external_id
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
        else:
            log.warning(
                "Case assignee not paged. No relationship between case type and an oncall service."
            )

    conversation_plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=case.project.id, plugin_type="conversation"
    )
    if conversation_plugin:
        if case.case_type.conversation_target:
            try:
                conversation = create_conversation(case, db_session)
                conversation_in = ConversationCreate(
                    resource_id=conversation["resource_id"],
                    resource_type=conversation["resource_type"],
                    weblink=conversation["weblink"],
                    thread_id=conversation["timestamp"],
                    channel_id=conversation["id"],
                )
                case.conversation = conversation_service.create(
                    db_session=db_session, conversation_in=conversation_in
                )

                event_service.log_case_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description="Conversation added to case",
                    case_id=case.id,
                )
                # wait until all resources are created before adding suggested participants
                individual_participants = [x.email for x, _ in individual_participants]

                for email in individual_participants:
                    # we don't rely on on this flow to add folks to the conversation because in this case
                    # we want to do it in bulk
                    case_add_or_reactivate_participant_flow(
                        db_session=db_session,
                        user_email=email,
                        case_id=case.id,
                        add_to_conversation=False,
                    )
                conversation_plugin.instance.add_to_thread(
                    case.conversation.channel_id,
                    case.conversation.thread_id,
                    individual_participants,
                )
                event_service.log_case_event(
                    db_session=db_session,
                    source="Dispatch Core App",
                    description="Incident participants added to case conversation.",
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

    db_session.add(case)
    db_session.commit()

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
def case_escalated_create_flow(
    *, case_id: int, organization_slug: OrganizationSlug, db_session=None
):
    """Runs the case escalated creation flow."""
    # we run the case new creation flow
    case_new_create_flow(
        case_id=case_id, organization_slug=organization_slug, db_session=db_session
    )

    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    # we transition the case to the triage state
    case_triage_status_flow(case=case, db_session=db_session)

    # we transition the case to the escalated state
    case_escalated_status_flow(
        case=case, organization_slug=organization_slug, db_session=db_session
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


@background_task
def case_update_flow(
    *,
    case_id: int,
    previous_case: CaseRead,
    assignee_email: str,
    user_email: str,
    organization_slug: OrganizationSlug,
    db_session=None,
):
    """Runs the case update flow."""
    # we get the case
    case = get(db_session=db_session, case_id=case_id)

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

    # we update the tactical group if we have a new assignee
    if previous_case.assignee.individual.email != assignee_email:
        log.debug(
            f"{user_email} updated Case {case_id} assignee from {previous_case.assignee.individual.email} to {assignee_email}"
        )
        case_assign_role_flow(
            case_id=case.id,
            assignee_email=assignee_email,
            assignee_role=ParticipantRoleType.assignee,
            db_session=db_session,
        )
        if case.tactical_group:
            group_flows.update_group(
                subject=case,
                group=case.tactical_group,
                group_action=GroupAction.add_member,
                group_member=case.assignee.individual.email,
                db_session=db_session,
            )
            event_service.log_case_event(
                db_session=db_session,
                source="Dispatch Core App",
                description="Case group updated",
                case_id=case_id,
            )

    # we send the case updated notification
    update_conversation(case, db_session)


def case_delete_flow(case: Case, db_session: SessionLocal):
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
    # we set the triage_at time
    case.triage_at = datetime.utcnow()
    db_session.add(case)
    db_session.commit()


def case_escalated_status_flow(case: Case, organization_slug: OrganizationSlug, db_session=None):
    """Runs the case escalated transition flow."""
    # we set the escalated_at time
    case.escalated_at = datetime.utcnow()
    db_session.add(case)
    db_session.commit()

    case_to_incident_escalate_flow(
        case=case, organization_slug=organization_slug, db_session=db_session
    )


def case_closed_status_flow(case: Case, db_session=None):
    """Runs the case closed transition flow."""
    # we set the closed_at time
    case.closed_at = datetime.utcnow()
    db_session.add(case)
    db_session.commit()


def case_status_transition_flow_dispatcher(
    case: Case,
    current_status: CaseStatus,
    previous_status: CaseStatus,
    organization_slug: OrganizationSlug,
    db_session: SessionLocal,
):
    """Runs the correct flows based on the current and previous status of the case."""
    # we changed the status of the case to new
    if current_status == CaseStatus.new:
        if previous_status == CaseStatus.triage:
            # Triage -> New
            pass
        elif previous_status == CaseStatus.escalated:
            # Escalated -> New
            pass
        elif previous_status == CaseStatus.closed:
            # Closed -> New
            pass

    # we changed the status of the case to triage
    elif current_status == CaseStatus.triage:
        if previous_status == CaseStatus.new:
            # New -> Triage
            case_triage_status_flow(case=case, db_session=db_session)
        elif previous_status == CaseStatus.escalated:
            # Escalated -> Triage
            pass
        elif previous_status == CaseStatus.closed:
            # Closed -> Triage
            pass

    # we changed the status of the case to escalated
    elif current_status == CaseStatus.escalated:
        if previous_status == CaseStatus.new:
            # New -> Escalated
            case_triage_status_flow(case=case, db_session=db_session)
            case_escalated_status_flow(
                case=case, organization_slug=organization_slug, db_session=db_session
            )
        elif previous_status == CaseStatus.triage:
            # Triage -> Escalated
            case_escalated_status_flow(
                case=case, organization_slug=organization_slug, db_session=db_session
            )
        elif previous_status == CaseStatus.closed:
            # Closed -> Escalated
            pass

    # we changed the status of the case to closed
    elif current_status == CaseStatus.closed:
        if previous_status == CaseStatus.new:
            # New -> Closed
            case_triage_status_flow(case=case, db_session=db_session)
            case_closed_status_flow(case=case, db_session=db_session)
        elif previous_status == CaseStatus.triage:
            # Triage -> Closed
            case_closed_status_flow(case=case, db_session=db_session)
        elif previous_status == CaseStatus.escalated:
            # Escalated -> Closed
            case_closed_status_flow(case=case, db_session=db_session)


def case_to_incident_escalate_flow(
    case: Case, organization_slug: OrganizationSlug, db_session=None
):
    """Escalates a case to an incident if the case's type is mapped to an incident type."""
    if case.incidents:
        # we don't escalate the case if the case is already linked to incidents
        return

    if not case.case_type.incident_type:
        # we don't escalate the case if its type is not mapped to an incident type
        return

    # we make the assignee of the case the reporter of the incident
    reporter = ParticipantUpdate(
        individual=IndividualContactRead(email=case.assignee.individual.email)
    )

    # we add information about the case in the incident's description
    description = (
        f"{case.description}\n\n"
        f"This incident was the result of escalating case {case.name} "
        f"in the {case.project.name} project. Check out the case in the Dispatch Web UI for additional context."
    )

    # we create the incident
    incident_in = IncidentCreate(
        title=case.title,
        description=description,
        status=IncidentStatus.active,
        incident_type=case.case_type.incident_type,
        incident_priority=case.case_priority,
        project=case.case_type.incident_type.project,
        reporter=reporter,
    )
    incident = incident_service.create(db_session=db_session, incident_in=incident_in)

    # we map the case to the newly created incident
    case.incidents.append(incident)

    # we run the incident creation flow
    incident_flows.incident_create_flow(
        incident_id=incident.id, organization_slug=organization_slug, db_session=db_session
    )

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description=f"The case has been linked to incident {incident.name} in the {incident.project.name} project",
        case_id=case.id,
    )

    # we add the incident's tactical group to the case's storage folder
    # to allow incident participants to access the case's artifacts in the folder
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
        description=f"The members of the incident's tactical group {incident.tactical_group.email} have been given permission to access the case's storage folder",
        case_id=case.id,
    )


@background_task
def case_to_incident_endpoint_escalate_flow(
    case_id: PrimaryKey,
    incident_id: PrimaryKey,
    organization_slug: OrganizationSlug,
    db_session=None,
):
    """Allows for a case to be escalated to an incident while modifying its properties."""
    # we get the case
    case = get(case_id=case_id, db_session=db_session)

    # we set the triage at time
    case_triage_status_flow(case=case, db_session=db_session)

    # we set the escalated at time and change the status to escalated
    case.escalated_at = datetime.utcnow()
    case.status = CaseStatus.escalated

    # we run the incident create flow
    incident = incident_flows.incident_create_flow(
        incident_id=incident_id, organization_slug=organization_slug, db_session=db_session
    )
    case.incidents.append(incident)

    db_session.add(case)
    db_session.commit()

    event_service.log_case_event(
        db_session=db_session,
        source="Dispatch Core App",
        description=f"The case has been linked to incident {incident.name} in the {incident.project.name} project",
        case_id=case.id,
    )

    # we add the incident's tactical group to the case's storage folder
    # to allow incident participants to access the case's artifacts in the folder
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
        description=f"The members of the incident's tactical group {incident.tactical_group.email} have been given permission to access the case's storage folder",
        case_id=case.id,
    )


def case_assign_role_flow(
    case_id: int,
    assignee_email: str,
    assignee_role: str,
    db_session: SessionLocal,
):
    """Runs the case participant role assignment flow."""
    case = get(case_id=case_id, db_session=db_session)

    # we add the assignee to the incident if they're not a participant
    case_add_or_reactivate_participant_flow(assignee_email, case.id, db_session=db_session)

    role_flow.assign_role_flow(case, assignee_email, assignee_role, db_session)
