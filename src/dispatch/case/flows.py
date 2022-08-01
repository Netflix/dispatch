import logging

from datetime import datetime

# from dispatch.case import service as case_service
from dispatch.case.models import CaseRead

# from dispatch.case_type import service as case_type_service
from dispatch.database.core import SessionLocal
from dispatch.decorators import background_task
from dispatch.case import service as case_service

# from dispatch.enums import Visibility
# from dispatch.event import service as event_service
# from dispatch.plugin import service as plugin_service
# from dispatch.ticket import flows as ticket_flows

from .models import Case, CaseStatus


log = logging.getLogger(__name__)


@background_task
def case_new_create_flow(*, case_id: int, organization_slug: str, db_session=None):
    """Runs the case new creation flow."""
    # NOTE: The following is temporary until the case is named after the ticket
    case = case_service.get(db_session=db_session, case_id=case_id)
    case.name = f"{case.id}-{case.title}"
    db_session.add(case)
    db_session.commit()


@background_task
def case_triage_create_flow(*, case_id: int, organization_slug: str = None, db_session=None):
    """Runs the case triage creation flow."""
    pass


@background_task
def case_escalated_create_flow(*, case_id: int, organization_slug: str = None, db_session=None):
    """Runs the case escalated creation flow."""
    pass


@background_task
def case_closed_create_flow(*, case_id: int, organization_slug: str = None, db_session=None):
    """Runs the case closed creation flow."""
    pass


@background_task
def case_update_flow(
    *,
    case_id: int,
    previous_case: CaseRead,
    user_email: str,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the case update flow."""
    # we fetch the case
    case = case_service.get(db_session=db_session, case_id=case_id)

    # we run the transition flow based on the current and previous status of the case
    case_status_transition_flow_dispatcher(
        case, case.status, previous_case.status, db_session=db_session
    )

    # we update the ticket
    # update_external_incident_ticket(incident_id, db_session)

    # we send the case updated notifications
    # send_case_update_notifications(case, previous_case, db_session)


def case_new_status_flow(case: Case, db_session=None):
    """Runs the case new transition flow."""
    pass


def case_triage_status_flow(case: Case, db_session=None):
    """Runs the case triage transition flow."""
    # we set the triage_at time
    case.triage_at = datetime.utcnow()
    db_session.add(case)
    db_session.commit()


def case_escalated_status_flow(case: Case, db_session=None):
    """Runs the case escalated transition flow."""
    # we set the escalated_at time
    case.escalated_at = datetime.utcnow()
    db_session.add(case)
    db_session.commit()


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
    db_session=SessionLocal,
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
            case_triage_status_flow(case, db_session)
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
            case_triage_status_flow(case, db_session)
            case_escalated_status_flow(case, db_session)
        elif previous_status == CaseStatus.triage:
            # Triage -> Escalated
            case_escalated_status_flow(case, db_session)
        elif previous_status == CaseStatus.closed:
            # Closed -> Escalated
            pass

    # we changed the status of the case to closed
    elif current_status == CaseStatus.closed:
        if previous_status == CaseStatus.new:
            # New -> Closed
            case_closed_status_flow(case, db_session)
        elif previous_status == CaseStatus.triage:
            # Triage -> Closed
            case_closed_status_flow(case, db_session)
        elif previous_status == CaseStatus.escalated:
            # Escalated -> Closed
            case_closed_status_flow(case, db_session)

    if previous_status != current_status:
        # event_service.log(
        #     db_session=db_session,
        #     source="Dispatch Core App",
        #     description=f"The incident status has been changed from {previous_status.lower()} to {current_status.lower()}",
        #     incident_id=incident.id,
        # )
        pass
