import logging

# from dispatch.case import service as case_service
from dispatch.case.models import CaseRead

# from dispatch.case_type import service as case_type_service
from dispatch.database.core import SessionLocal
from dispatch.decorators import background_task

# from dispatch.enums import Visibility
# from dispatch.event import service as event_service
# from dispatch.plugin import service as plugin_service
# from dispatch.ticket import flows as ticket_flows

from .models import Case, CaseStatus


log = logging.getLogger(__name__)


@background_task
def case_new_create_flow(*, organization_slug: str, case_id: int, db_session=None):
    """Runs the case new creation flow."""
    pass


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
    case_id: int,
    previous_case: CaseRead,
    organization_slug: str = None,
    db_session=None,
):
    """Runs the case update flow."""
    pass


def case_new_status_flow(case: Case, db_session=None):
    """Runs the case new transition flow."""
    pass


def case_triage_status_flow(case: Case, db_session=None):
    """Runs the case triage transition flow."""
    pass


def case_escalated_status_flow(case: Case, db_session=None):
    """Runs the case escalated transition flow."""
    pass


def case_closed_status_flow(case: Case, db_session=None):
    """Runs the case closed transition flow."""
    pass


def status_flow_dispatcher(
    case: Case,
    current_status: CaseStatus,
    previous_status: CaseStatus,
    db_session=SessionLocal,
):
    """Runs the correct flows depending on the case's current and previous status."""
    pass
