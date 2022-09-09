from dispatch.database.core import SessionLocal
from dispatch.case import service as case_service


def create_case(signal, db_session: SessionLocal):
    """Creates a case from a signal."""
    # do no create a case for duplicate or supressed signals
    if signal.duplicate or signal.supressed:
        return

    case = signal
    return case_service.create(db_session, case_in=case)
