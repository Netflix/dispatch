def test_get(session, report):
    from dispatch.report.service import get

    t_report = get(db_session=session, report_id=report.id)
    assert t_report.id == report.id


def test_get_all(session, reports):
    from dispatch.report.service import get_all

    t_reports = get_all(db_session=session).all()
    assert t_reports


def test_create(session):
    from dispatch.report.service import create
    from dispatch.report.models import ReportCreate

    details = {"conditions": "conditions", "actions": "actions", "needs": "needs"}
    type = "Tactical Report"

    report_in = ReportCreate(
        details=details,
        type=type,
    )
    report = create(db_session=session, report_in=report_in)
    assert report


def test_update(session, report):
    from dispatch.report.service import update
    from dispatch.report.models import ReportUpdate

    details = {
        "conditions": "updated conditions",
        "actions": "updated actions",
        "needs": "updated needs",
    }
    type = "Tactical Report"

    report_in = ReportUpdate(details=details, type=type)
    report = update(
        db_session=session,
        report=report,
        report_in=report_in,
    )
    assert report.details["conditions"] == details["conditions"]


def test_delete(session, report):
    from dispatch.report.service import delete, get

    delete(db_session=session, report_id=report.id)
    assert not get(db_session=session, report_id=report.id)
