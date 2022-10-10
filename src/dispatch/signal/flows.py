from dispatch.case.models import CaseCreate
from dispatch.database.core import SessionLocal
from dispatch.case import service as case_service
from dispatch.case import flows as case_flows
from dispatch.signal import service as signal_service
from dispatch.signal.duplication_rule import service as duplication_service
from dispatch.signal.models import SignalInstanceRead
from dispatch.signal.suppression_rule import service as suppression_service


def create_signal_instance(db_session: SessionLocal, signal_instance_in: SignalInstanceRead):
    """Creates a signal and a case if necessary."""
    signal_instance = signal_service.create_instance(
        db_session=db_session, signal_instance_in=signal_instance_in
    )

    suppressed = suppression_service.supress(db_session=db_session, signal_instance=signal_instance)
    if suppressed:
        return

    duplicate = duplication_service.deduplicate(
        db_session=db_session, signal_instance=signal_instance
    )
    if duplicate:
        return

    # create a case if not duplicate or supressed
    case_in = CaseCreate(
        title=signal_instance.signal.name, description="Automatically created based on signal."
    )
    case = case_service.create(db_session=db_session, case_in=case_in)
    case.signal_instances.append(signal_instance)
    return case_flows.case_new_create_flow(
        db_session=db_session, organization_slug=None, case_id=case.id
    )
