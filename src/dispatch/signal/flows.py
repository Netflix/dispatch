from dispatch.case.models import CaseCreate
from dispatch.database.core import SessionLocal
from dispatch.case import service as case_service
from dispatch.case import flows as case_flows
from dispatch.signal import service as signal_service
from dispatch.signal.models import SignalInstanceRead


def create_signal_instance(
    db_session: SessionLocal, external_id: str, variant: str, signal_instance_in: SignalInstanceRead
):
    """Creates a signal and a case if necessary."""
    signal = signal_service.get_by_external_id_and_variant(
        db_session=db_session,
        external_id=external_id,
        variant=variant,
    )

    signal_instance = signal_service.create_instance(
        db_session=db_session, signal_instance_in=signal_instance_in
    )

    signal_instance.signal = signal

    suppressed = signal_service.supress(
        db_session=db_session,
        signal_instance=signal_instance,
        suppression_rule=signal.suppression_rule,
    )
    if suppressed:
        return

    duplicate = signal_service.deduplicate(
        db_session=db_session,
        signal_instance=signal_instance,
        duplication_rule=signal.duplication_rule,
    )
    if duplicate:
        return

    # create a case if not duplicate or supressed
    case_in = CaseCreate(
        title=signal.name,
        description=signal.description,
        case_priority=signal.case_priority,
        case_type=signal.case_type,
    )
    case = case_service.create(db_session=db_session, case_in=case_in)
    return case_flows.case_new_create_flow(
        db_session=db_session, organization_slug=None, case_id=case.id
    )
