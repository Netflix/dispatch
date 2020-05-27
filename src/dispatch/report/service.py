from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from .enums import ReportTypes
from .models import Report, ReportCreate, ReportUpdate


def get(*, db_session, report_id: int) -> Optional[Report]:
    """
    Get a report by id.
    """
    return db_session.query(Report).filter(Report.id == report_id).one_or_none()


def get_most_recent_by_incident_id_and_type(
    *, db_session, incident_id: int, report_type: ReportTypes
) -> Optional[Report]:
    """
    Get most recent report by incident id and report type.
    """
    return (
        db_session.query(Report)
        .filter(Report.incident_id == incident_id)
        .filter(Report.type == report_type)
        .order_by(Report.created_at.desc())
        .first()
    )


def get_all_by_incident_id_and_type(
    *, db_session, incident_id: int, report_type: ReportTypes
) -> Optional[Report]:
    """
    Get all reports by incident id and report type.
    """
    return (
        db_session.query(Report)
        .filter(Report.incident_id == incident_id)
        .filter(Report.type == report_type)
    )


def get_all_by_type(*, db_session, report_type: ReportTypes) -> List[Optional[Report]]:
    """
    Get all reports by type.
    """
    return db_session.query(Report).filter(Report.type == report_type)


def get_all(*, db_session) -> List[Optional[Report]]:
    """
    Get all reports.
    """
    return db_session.query(Report)


def create(*, db_session, report_in: ReportCreate) -> Report:
    """
    Create a new report.
    """
    report = Report(**report_in.dict())
    db_session.add(report)
    db_session.commit()
    return report


def update(*, db_session, report: Report, report_in: ReportUpdate) -> Report:
    """Updates a report."""
    report_data = jsonable_encoder(report)
    update_data = report_in.dict(skip_defaults=True)

    for field in report_data:
        if field in update_data:
            setattr(report, field, update_data[field])

    db_session.add(report)
    db_session.commit()
    return report


def delete(*, db_session, report_id: int):
    """Deletes a report."""
    db_session.query(Report).filter(Report.id == report_id).delete()
    db_session.commit()
