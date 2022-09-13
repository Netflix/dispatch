from dispatch.case.models import CaseCreate
from dispatch.database.core import SessionLocal
from dispatch.case import flows as case_flows
from dispatch.case import service as case_service
from dispatch.signal import service as signal_service
from dispatch.signal.duplication_rule import service as duplication_service
from dispatch.signal.models import SignalRead
from dispatch.signal.suppression_rule import service as suppression_service


def create_signal(db_session: SessionLocal, signal_in: SignalRead):
    """Creates a signal and a case if necessary."""
    # don't create "hard duplicates" due to sync issues (e.g. external_id + source)
    match = signal_service.match(db_session=db_session, signal_in=signal_in)
    if match:
        return

    signal = signal_service.create(db_session=db_session, signal_in=signal_in)
    match = duplication_service.match(db_session=db_session, signal=signal_in)
    if match:
        signal.duplicate = True
        signal.duplication_rule_id = match.id
        return

    match = suppression_service.match(db_session=db_session, signal=signal)
    if match:
        signal.supressed = True
        signal.suppression_rule_id = match.id
        return

    case_in = CaseCreate(title=signal.name, description="Automatically created based on signal.")
    case = case_service.create(db_session=db_session, case_in=case_in)
    return case_flows.case_new_create_flow(db_session=db_session, case_id=case.id)
