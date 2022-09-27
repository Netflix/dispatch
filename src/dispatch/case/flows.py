import logging

from datetime import datetime

from dispatch.case.models import CaseRead
from dispatch.database.core import SessionLocal
from dispatch.decorators import background_task
from dispatch.document import flows as document_flows
from dispatch.enums import DocumentResourceTypes
from dispatch.event import service as event_service
from dispatch.group import flows as group_flows
from dispatch.group.enums import GroupType, GroupAction
from dispatch.incident import flows as incident_flows
from dispatch.incident import service as incident_service
from dispatch.incident.enums import IncidentStatus
from dispatch.incident.models import IncidentCreate
from dispatch.individual.models import IndividualContactRead
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.participant.models import ParticipantUpdate
from dispatch.storage import flows as storage_flows
from dispatch.storage.enums import StorageAction
from dispatch.ticket import flows as ticket_flows

from .models import Case, CaseStatus
from .service import get, delete


log = logging.getLogger(__name__)


@background_task
def case_new_create_flow(*, case_id: int, organization_slug: OrganizationSlug, db_session=None):
    """Runs the case new creation flow."""
    # we get the case
    case = get(db_session=db_session, case_id=case_id)

    # we create the ticket
    ticket = ticket_flows.create_case_ticket(case=case, db_session=db_session)

    if not ticket:
        # we delete the case
        delete(db_session=db_session, case_id=case_id)

        return

    # we create the tactical group
    group_participants = [case.assignee.email]
    group = group_flows.create_group(
        obj=case,
        group_type=GroupType.tactical,
        group_participants=group_participants,
        db_session=db_session,
    )

    if not group:
        # we delete the ticket
        ticket_flows.delete_ticket(ticket=ticket, db_session=db_session)

        # we delete the case
        delete(db_session=db_session, case_id=case_id)

        return

    # we create the storage folder
    storage_members = [group.email]
    storage = storage_flows.create_storage(
        obj=case, storage_members=storage_members, db_session=db_session
    )
    if not storage:
        # we delete the group
        group_flows.delete_group(group=group, db_session=db_session)

        # we delete the ticket
        ticket_flows.delete_ticket(ticket=ticket, db_session=db_session)

        # we delete the case
        delete(db_session=db_session, case_id=case_id)

        return

    # we create the investigation document
    document = document_flows.create_document(
        obj=case,
        document_type=DocumentResourceTypes.case,
        document_template=case.case_type.case_template_document,
        db_session=db_session,
    )
    if not document:
        # we delete the storage
        storage_flows.delete_storage(storage=storage, db_session=db_session)

        # we delete the group
        group_flows.delete_group(group=group, db_session=db_session)

        # we delete the ticket
        ticket_flows.delete_ticket(ticket=ticket, db_session=db_session)

        # we delete the case
        delete(db_session=db_session, case_id=case_id)

        return

    # we update the ticket
    ticket_flows.update_case_ticket(case=case, db_session=db_session)

    # we update the case document
    document_flows.update_document(
        document=document, project_id=case.project.id, db_session=db_session
    )

    # TODO(mvilanova): we send the case created notification

    db_session.add(case)
    db_session.commit()


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
    if previous_case.assignee.email != case.assignee.email:
        group_flows.update_group(
            obj=case,
            group=case.tactical_group,
            group_action=GroupAction.add_member,
            group_member=case.assignee.email,
            db_session=db_session,
        )

    # we send the case updated notification


def case_delete_flow(case: Case, db_session: SessionLocal):
    """Runs the case delete flow."""
    # we delete the external ticket
    if case.ticket:
        ticket_flows.delete_ticket(ticket=case.ticket, db_session=db_session)

    # we delete the external groups
    if case.groups:
        for group in case.groups:
            group_flows.delete_group(group=group, db_session=db_session)

    # we delete the external storage
    if case.storage:
        storage_flows.delete_storage(storage=case.storage, db_session=db_session)


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
    incident_service.create(db_session=db_session, incident_in=incident_in)

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
    reporter = ParticipantUpdate(individual=IndividualContactRead(email=case.assignee.email))

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
        obj=case,
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
    case = get(case_id=case_id, db_session=db_session)
    incident = incident_flows.incident_create_flow(incident_id=incident_id, db_session=db_session)

    case.escalated_at = datetime.utcnow()
    case.status = CaseStatus.escalated
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
        obj=case,
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
