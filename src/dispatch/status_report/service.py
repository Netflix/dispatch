from typing import Optional

from .models import StatusReport


def get(*, db_session, status_report_id: int) -> Optional[StatusReport]:
    """
    Get a status report by id.
    """
    return db_session.query(StatusReport).filter(StatusReport.id == status_report_id).first()


def get_most_recent_by_incident_id(*, db_session, incident_id: int) -> Optional[StatusReport]:
    """
    Get last status report by incident id.
    """
    return (
        db_session.query(StatusReport)
        .filter(StatusReport.incident_id == incident_id)
        .order_by(StatusReport.created_at.desc())
        .first()
    )


def get_all(*, db_session):
    """
    Get all status reports.
    """
    return db_session.query(StatusReport)


def create(*, db_session, conditions: str, actions: str, needs: str) -> StatusReport:
    """
    Create a new status report.
    """
    status_report = StatusReport(conditions=conditions, actions=actions, needs=needs)
    db_session.add(status_report)
    db_session.commit()
    return status_report
