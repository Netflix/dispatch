from dispatch.case.models import CaseCreate
from dispatch.database.core import SessionLocal
from dispatch.case import service as case_service
from dispatch.case import flows as case_flows
from dispatch.signal import service as signal_service
from dispatch.signal.models import SignalInstanceCreate


def create_signal_instance(db_session: SessionLocal, signal_instance_data: dict):
    """Creates a signal and a case if necessary."""
    signal = signal_service.get_by_variant_or_external_id(
        db_session=db_session,
        external_id=signal_instance_data.id,
        variant=signal_instance_data.variant,
    )
    signal_instance_in = SignalInstanceCreate(**signal_instance_data, project=signal.project)

    signal_instance = signal_service.create_instance(
        db_session=db_session, signal_instance_in=signal_instance_in
    )

    signal_instance.signal = signal
    db_session.commit()

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

    signal_instance.case = case
    db_session.commit()
    return case_flows.case_new_create_flow(
        db_session=db_session, organization_slug=None, case_id=case.id
    )
