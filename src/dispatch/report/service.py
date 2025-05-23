
from .enums import ReportTypes
from .models import Report, ReportCreate, ReportUpdate


def get(*, db_session, report_id: int) -> Report | None:
    """Get a report by id."""
    return db_session.query(Report).filter(Report.id == report_id).one_or_none()


def get_most_recent_by_incident_id_and_type(
    *, db_session, incident_id: int, report_type: ReportTypes
) -> Report | None:
    """Get most recent report by incident id and report type."""
    return (
        db_session.query(Report)
        .filter(Report.incident_id == incident_id)
        .filter(Report.type == report_type)
        .order_by(Report.created_at.desc())
        .first()
    )


def get_all_by_incident_id_and_type(
    *, db_session, incident_id: int, report_type: ReportTypes
) -> Report | None:
    """Get all reports by incident id and report type."""
    return (
        db_session.query(Report)
        .filter(Report.incident_id == incident_id)
        .filter(Report.type == report_type)
    )


def get_all(*, db_session) -> list[Report | None]:
    """Get all reports."""
    return db_session.query(Report)


def create(*, db_session, report_in: ReportCreate) -> Report:
    """Create a new report."""
    report = Report(**report_in.dict())
    db_session.add(report)
    db_session.commit()
    return report


def update(*, db_session, report: Report, report_in: ReportUpdate) -> Report:
    """Updates a report."""
    report_data = report.dict()
    update_data = report_in.dict(exclude_unset=True)

    for field in report_data:
        if field in update_data:
            setattr(report, field, update_data[field])

    db_session.commit()
    return report


def delete(*, db_session, report_id: int):
    """Deletes a report."""
    db_session.query(Report).filter(Report.id == report_id).delete()
    db_session.commit()
