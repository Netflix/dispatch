def test_create_tactical_report(session, incident, participant):
    from dispatch.report.flows import create_tactical_report
    from dispatch.report.models import TacticalReportCreate

    participant.incident = incident

    tactical_report_in = TacticalReportCreate(
        conditions="sample conditions", actions="sample actions", needs="sample needs"
    )

    assert create_tactical_report(
        user_email=participant.individual.email,
        incident_id=participant.incident.id,
        tactical_report_in=tactical_report_in,
        organization_slug=incident.project.organization.slug,
        db_session=session,
    )
