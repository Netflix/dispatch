def test_case_messaging(session, case):
    from dispatch.case.messaging import send_case_close_reminder
    from dispatch.case import service as case_service
    from dispatch.case.enums import CaseStatus

    case.status = CaseStatus.triage
    t_case = case_service.get_all_by_status(
        db_session=session, project_id=case.project.id, statuses=[CaseStatus.new, CaseStatus.triage]
    )
    send_case_close_reminder(case=t_case[0], db_session=session)
    pass
