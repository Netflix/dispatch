def test_update_case_triage(session, case, user):
    """Tests the update of a case to triage status."""
    from fastapi import FastAPI, BackgroundTasks
    from fastapi.testclient import TestClient
    from dispatch.case import service as case_service
    from dispatch.case.enums import CaseStatus
    from dispatch.case.models import CaseUpdate, CaseRead
    from dispatch.case.views import update_case, router

    app = FastAPI()
    app.include_router(router, prefix=f"/{case.project.organization.slug}/cases", tags=["cases"])
    client = TestClient(app)

    @app.get("/{case_id}", response_model=CaseRead)
    async def views_update_case(background_tasks: BackgroundTasks):
        case_in = CaseUpdate.from_orm(case)
        case_in.status = CaseStatus.triage
        return update_case(
            db_session=session,
            current_case=case,
            organization=case.project.organization,
            case_id=case.id,
            case_in=case_in,
            current_user=user,
            background_tasks=background_tasks,
        )

    client.get(f"/{case.id}")
    t_case = case_service.get(db_session=session, case_id=case.id)
    assert t_case.status == CaseStatus.triage


def test_update_case_closed(session, case, user):
    """Tests the update of a case to closed status."""
    from fastapi import FastAPI, BackgroundTasks
    from fastapi.testclient import TestClient
    from dispatch.case import service as case_service
    from dispatch.case.enums import CaseStatus
    from dispatch.case.models import CaseUpdate, CaseRead
    from dispatch.case.views import update_case, router

    app = FastAPI()
    app.include_router(router, prefix=f"/{case.project.organization.slug}/cases", tags=["cases"])
    client = TestClient(app)

    @app.get("/{case_id}", response_model=CaseRead)
    async def views_update_case(background_tasks: BackgroundTasks):
        case_in = CaseUpdate.from_orm(case)
        case_in.status = CaseStatus.closed
        return update_case(
            db_session=session,
            current_case=case,
            organization=case.project.organization,
            case_id=case.id,
            case_in=case_in,
            current_user=user,
            background_tasks=background_tasks,
        )

    client.get(f"/{case.id}")
    t_case = case_service.get(db_session=session, case_id=case.id)
    assert t_case.status == CaseStatus.closed


def test_update_case_escalated(session, case, user):
    """Tests the update of a case to escalated status.

    There is a known bug where cases can be escalated in the UI without creating an incident."""
    from fastapi import FastAPI, BackgroundTasks
    from fastapi.testclient import TestClient
    from dispatch.case.views import update_case, router
    from dispatch.case.enums import CaseStatus
    from dispatch.case.models import CaseUpdate, CaseRead
    from dispatch.case import service as case_service

    app = FastAPI()
    app.include_router(router, prefix=f"/{case.project.organization.slug}/cases", tags=["cases"])
    client = TestClient(app)

    @app.get("/{case_id}", response_model=CaseRead)
    async def views_update_case(background_tasks: BackgroundTasks):
        case_in = CaseUpdate.from_orm(case)
        case_in.status = CaseStatus.escalated
        return update_case(
            db_session=session,
            current_case=case,
            organization=case.project.organization,
            case_id=case.id,
            case_in=case_in,
            current_user=user,
            background_tasks=background_tasks,
        )

    client.get(f"/{case.id}")
    t_case = case_service.get(db_session=session, case_id=case.id)
    assert t_case.status == CaseStatus.escalated


def test_case_escalated_create_incident(session, case, user, incident):
    """Tests the escalation of a case to an incident."""
    from fastapi import FastAPI, BackgroundTasks
    from fastapi.testclient import TestClient
    from dispatch.case.views import router, escalate_case
    from dispatch.case.enums import CaseStatus
    from dispatch.case import service as case_service
    from dispatch.incident.enums import IncidentStatus
    from dispatch.incident.models import IncidentCreate, IncidentRead

    # Initial setup.
    case.case_type.project = case.project
    case.case_priority.project = case.project
    case.case_severity.project = case.project

    incident.project = case.project
    incident.incident_type.project = case.project
    incident.incident_priority.project = case.project
    incident.incident_severity.project = case.project

    app = FastAPI()
    app.include_router(router, prefix=f"/{case.project.organization.slug}/cases", tags=["cases"])

    @app.get("/{case_id}/escalate", response_model=IncidentRead)
    async def views_escalate_case(background_tasks: BackgroundTasks):

        incident_in = IncidentCreate.from_orm(incident)
        incident_in.status = IncidentStatus.active
        incident_in.title = case.title

        incident_out = escalate_case(
            db_session=session,
            current_case=case,
            organization=case.project.organization,
            incident_in=incident_in,
            current_user=user,
            background_tasks=background_tasks,
        )

        return incident_out

    client = TestClient(app)
    client.get(f"/{case.id}/escalate")

    case_t = case_service.get(db_session=session, case_id=case.id)
    assert case_t.status == CaseStatus.escalated
    assert len(case_t.incidents)
    assert case_t.incidents[0].title == case.title
