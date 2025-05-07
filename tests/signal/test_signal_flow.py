from unittest import mock

import pytest

from dispatch.exceptions import DispatchException
from dispatch.case.models import CaseReadMinimal, ProjectRead as CaseProjectRead
from dispatch.service.models import ServiceRead
from dispatch.project.models import ProjectRead as ProjectReadProject
from dispatch.case.models import ProjectRead as ProjectReadCase
from dispatch.signal.models import (
    SignalInstanceCreate,
    CaseReadMinimal as SignalCaseReadMinimal,
    CasePriorityRead as SignalCasePriorityRead,
    CaseTypeRead as SignalCaseTypeRead,
    ProjectRead as SignalProjectRead,
    ServiceRead as SignalServiceRead,
)
from dispatch.case.severity.models import CaseSeverityRead
from dispatch.case.type.models import CaseType
from dispatch.case.priority.models import CasePriorityRead
from dispatch.case.type.models import CaseTypeRead


def test_create_signal_instance(session, signal, case_severity, case_priority, user, services):
    from dispatch.signal.flows import create_signal_instance
    from dispatch.case.priority.models import CasePriorityRead
    from dispatch.case.type.models import CaseTypeRead
    from dispatch.case.severity.models import CaseSeverityRead
    from dispatch.project.models import ProjectRead as SignalProjectRead
    from dispatch.service.models import ServiceRead
    from dispatch.case.models import CaseReadMinimal, ProjectRead as ProjectReadCase

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    # Ensure the 'Default' case type exists in the DB
    case_type_db = CaseType(
        name="Default",
        project_id=signal.project_id,
        enabled=True,
    )
    session.add(case_type_db)
    session.commit()

    # Use ProjectReadProject for CasePriorityRead, CaseTypeRead, CaseSeverityRead
    project_read_project = ProjectReadProject(
        id=signal.project.id,
        name=signal.project.name,
        display_name="Test Project",
        color=None,
        allow_self_join=True,
        owner_email=None,
        owner_conversation=None,
        annual_employee_cost=0,
        business_year_hours=0,
        snooze_extension_oncall_service=None,
        description=None,
        send_daily_reports=False,
        send_weekly_reports=False,
        weekly_report_notification_id=None,
        enabled=True,
        storage_folder_one=None,
        storage_folder_two=None,
        storage_use_folder_one_as_primary=False,
        storage_use_title=False,
        select_commander_visibility=False,
        report_incident_instructions=None,
        report_incident_title_hint=None,
        report_incident_description_hint=None,
    )
    # Use ProjectReadCase for CaseReadMinimal
    project_read_case = ProjectReadCase(
        id=signal.project.id,
        name=signal.project.name,
        display_name="Test Project",
        color=None,
        allow_self_join=True,
    )
    case_priority_read = CasePriorityRead(
        id=case_priority.id,
        name=case_priority.name,
        color=None,
        default=True,
        page_assignee=False,
        description=None,
        enabled=True,
        project=project_read_project,
        view_order=1,
    )
    case_type_read = CaseTypeRead(
        id=signal.case_type.id,
        name=signal.case_type.name,
        description=None,
        visibility=None,
        default=False,
        enabled=True,
        exclude_from_metrics=False,
        plugin_metadata=[],
        conversation_target=None,
        auto_close=False,
        case_template_document=None,
        oncall_service=None,
        incident_type=None,
        project=project_read_project,
        cost_model=None,
    )
    case_severity_read = CaseSeverityRead(
        id=1,
        name="Low",
        color=None,
        default=True,
        description=None,
        enabled=True,
        project=project_read_project,
        view_order=1,
    )
    case_read_minimal = CaseReadMinimal(
        id=1,
        name="Test Case",
        title="Test Case",
        description="desc",
        resolution=None,
        resolution_reason=None,
        status=None,
        visibility=None,
        closed_at=None,
        reported_at=None,
        dedicated_channel=None,
        case_type=case_type_read,
        case_severity=case_severity_read,
        case_priority=case_priority_read,
        project=project_read_case,
        assignee=None,
        case_costs=[],
    )
    service_0, service_1 = services
    service_0.project_id = signal.project_id
    service_1.project_id = signal.project_id
    service_read = ServiceRead(
        id=service_1.id,
        description=service_1.description,
        external_id=service_1.external_id,
        is_active=service_1.is_active,
        name=service_1.name,
        type=service_1.type,
        shift_hours_type=service_1.shift_hours_type,
    )

    instance_data = {
        "variant": signal.variant,
        "case": case_read_minimal.dict(),
        "external_id": "test-external-id",
        "case_priority": case_priority_read.dict(),
        "case_type": case_type_read.dict(),
        "conversation_target": None,
        "oncall_service": service_read.dict(),
    }

    assert create_signal_instance(
        db_session=session,
        project=signal.project,
        signal_instance_data=instance_data,
        current_user=user,
    )


def test_create_signal_instance_no_variant(session, signal, case_severity, case_priority, user, services):
    from dispatch.signal.flows import create_signal_instance

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    instance_data = {"variant": "unknown"}
    with pytest.raises(DispatchException):
        create_signal_instance(
            db_session=session,
            project=signal.project,
            signal_instance_data=instance_data,
            current_user=user,
        )


def test_create_signal_instance_not_enabled(session, signal, case_severity, case_priority, user, services):
    from dispatch.signal.flows import create_signal_instance

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    signal.enabled = False
    instance_data = {"variant": signal.variant}
    with pytest.raises(DispatchException):
        create_signal_instance(
            db_session=session,
            project=signal.project,
            signal_instance_data=instance_data,
            current_user=user,
        )

def test_create_signal_instance_custom_conversation_target(session, signal, case_severity, case_priority, user, case_type, services):
    from dispatch.signal.flows import create_signal_instance
    from dispatch.case.priority.models import CasePriorityRead
    from dispatch.case.type.models import CaseTypeRead
    from dispatch.project.models import ProjectRead
    from dispatch.case.models import CaseReadMinimal
    from dispatch.service.models import ServiceRead
    from dispatch.case.severity.models import CaseSeverityRead
    from dispatch.case.models import ProjectRead as CaseProjectRead

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    service_0, service_1 = services
    service_0.project_id = signal.project_id
    service_1.project_id = signal.project_id

    # Ensure the case_type exists in the DB with the correct name and project_id
    case_type.name = "test-case-type"
    case_type.project_id = signal.project_id
    case_type.enabled = True
    session.add(case_type)
    session.commit()

    project_read_signal = SignalProjectRead(
        id=signal.project.id,
        name=signal.project.name,
        display_name="Test Project",
        color=None,
        allow_self_join=True,
        owner_email=None,
        owner_conversation=None,
        annual_employee_cost=0,
        business_year_hours=0,
        snooze_extension_oncall_service=None,
        description=None,
        send_daily_reports=False,
        send_weekly_reports=False,
        weekly_report_notification_id=None,
        enabled=True,
        storage_folder_one=None,
        storage_folder_two=None,
        storage_use_folder_one_as_primary=False,
        storage_use_title=False,
        select_commander_visibility=False,
        report_incident_instructions=None,
        report_incident_title_hint=None,
        report_incident_description_hint=None,
    )
    case_priority_read = SignalCasePriorityRead(
        id=1,
        name=case_priority.name,
        color=None,
        default=True,
        page_assignee=False,
        description=None,
        enabled=True,
        project=project_read_signal,
        view_order=1,
    )
    case_type_read = SignalCaseTypeRead(id=1, name=case_type.name, project=project_read_signal)
    case_severity_read = CaseSeverityRead(
        id=1,
        name="Low",
        color=None,
        default=True,
        description=None,
        enabled=True,
        project=project_read_signal,
        view_order=1,
    )
    case_read_minimal = SignalCaseReadMinimal(
        id=1,
        name="Test Case",
        title="Test Case",
        description="desc",
        resolution=None,
        resolution_reason=None,
        status=None,
        visibility=None,
        closed_at=None,
        reported_at=None,
        dedicated_channel=None,
        case_type=case_type_read,
        case_severity=case_severity_read,
        case_priority=case_priority_read,
        project=project_read_signal,
        assignee=None,
        case_costs=[],
    )
    service_0, service_1 = services
    service_read = ServiceRead(
        id=service_1.id,
        description=service_1.description,
        external_id=service_1.external_id,
        is_active=service_1.is_active,
        name=service_1.name,
        type=service_1.type,
        shift_hours_type=service_1.shift_hours_type,
    )

    instance_data = {
        "variant": signal.variant,
        "case": case_read_minimal.dict(),
        "external_id": "test-external-id",
        "case_priority": case_priority_read.dict(),
        "case_type": case_type_read.dict(),
        "conversation_target": "test-conversation-target",
        "oncall_service": service_read.dict(),
    }
    signal.conversation_target = "signal-conversation-target"

    signal_instance = create_signal_instance(
        db_session=session,
        project=signal.project,
        signal_instance_data=instance_data,
        current_user=user,
    )
    assert signal_instance.conversation_target == 'test-conversation-target'


def test_create_signal_instance_custom_oncall_service(session, signal, case_severity, case_priority, user, services):
    from dispatch.signal.flows import create_signal_instance
    from dispatch.case.priority.models import CasePriorityRead
    from dispatch.case.type.models import CaseTypeRead
    from dispatch.case.models import CaseReadMinimal, ProjectRead as ProjectReadCase
    from dispatch.project.models import ProjectRead as ProjectReadProject

    service_0, service_1 = services
    service_0.project_id = signal.project_id
    service_1.project_id = signal.project_id

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    # Ensure both services are in the DB
    session.add_all([service_0, service_1])
    session.commit()
    # Use ProjectReadProject for CaseReadMinimal
    project_read_project = ProjectReadProject(
        id=signal.project.id,
        name=signal.project.name,
        display_name="Test Project",
        color=None,
        allow_self_join=True,
        owner_email=None,
        owner_conversation=None,
        annual_employee_cost=0,
        business_year_hours=0,
        snooze_extension_oncall_service=None,
        description=None,
        send_daily_reports=False,
        send_weekly_reports=False,
        weekly_report_notification_id=None,
        enabled=True,
        storage_folder_one=None,
        storage_folder_two=None,
        storage_use_folder_one_as_primary=False,
        storage_use_title=False,
        select_commander_visibility=False,
        report_incident_instructions=None,
        report_incident_title_hint=None,
        report_incident_description_hint=None,
    )
    project_read_case = ProjectReadCase(
        id=signal.project.id,
        name=signal.project.name,
        display_name="Test Project",
        color=None,
        allow_self_join=True,
    )
    case_priority_read = CasePriorityRead(
        id=case_priority.id,
        name=case_priority.name,
        color=None,
        default=True,
        page_assignee=False,
        description=None,
        enabled=True,
        project=project_read_project,
        view_order=1,
    )
    case_type_read = CaseTypeRead(
        id=signal.case_type.id,
        name=signal.case_type.name,
        description=None,
        visibility=None,
        default=False,
        enabled=True,
        exclude_from_metrics=False,
        plugin_metadata=[],
        conversation_target=None,
        auto_close=False,
        case_template_document=None,
        oncall_service=None,
        incident_type=None,
        project=project_read_project,
        cost_model=None,
    )
    case_severity_read = CaseSeverityRead(
        id=1,
        name="Low",
        color=None,
        default=True,
        description=None,
        enabled=True,
        project=project_read_project,
        view_order=1,
    )
    case_read_minimal = CaseReadMinimal(
        id=1,
        name="Test Case",
        title="Test Case",
        description="desc",
        resolution=None,
        resolution_reason=None,
        status=None,
        visibility=None,
        closed_at=None,
        reported_at=None,
        dedicated_channel=None,
        case_type=case_type_read,
        case_severity=case_severity_read,
        case_priority=case_priority_read,
        project=project_read_case,
        assignee=None,
        case_costs=[],
    )
    service_read = ServiceRead(
        id=service_1.id,
        description=service_1.description,
        external_id=service_1.external_id,
        is_active=service_1.is_active,
        name=service_1.name,
        type=service_1.type,
        shift_hours_type=service_1.shift_hours_type,
    )

    instance_data = {
        "variant": signal.variant,
        "case": case_read_minimal.dict(),
        "external_id": "test-external-id",
        "case_priority": case_priority_read.dict(),
        "case_type": case_type_read.dict(),
        "conversation_target": None,
        "oncall_service": service_read.dict(),
    }

    signal_instance = create_signal_instance(
        db_session=session,
        project=signal.project,
        signal_instance_data=instance_data,
        current_user=user,
    )
    assert signal_instance.oncall_service is not None, "signal_instance.oncall_service is None"
    assert signal_instance.oncall_service.id == service_1.id

def test_signal_instance_create_flow_custom_attributes(session, signal, case_severity, case_priority, user, services, signal_instance, oncall_plugin, case_type, case):
    from dispatch.signal.flows import signal_instance_create_flow
    from dispatch.service import flows as service_flows
    from dispatch.case import service as case_service

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    service_0, service_1 = services
    service_0.project_id = signal.project_id
    service_1.project_id = signal.project_id

    signal_instance.oncall_service = service_0
    signal_instance.signal.oncall_service = service_1
    signal_instance.conversation_target = "instance-conversation-target"
    signal_instance.signal.conversation_target = "signal-conversation-target"

    with mock.patch.object(service_flows, "resolve_oncall") as mock_resolve_oncall, \
        mock.patch.object(case_service, "create") as mock_case_create, \
        mock.patch("dispatch.case.flows.case_new_create_flow") as mock_case_new_create_flow:
        mock_resolve_oncall.side_effect = lambda service, db_session: "example@test.com" if service.id == service_0.id else None
        mock_case_create.return_value = case

        post_flow_instance = signal_instance_create_flow(
            signal_instance_id=signal_instance.id,
            db_session=session,
            current_user=user
        )
        case_in_arg = mock_case_create.call_args[1]['case_in']
        assert case_in_arg.assignee.individual.email == "example@test.com"
        if post_flow_instance is not None and hasattr(post_flow_instance, "case") and post_flow_instance.case is not None:
            mock_case_new_create_flow.assert_called_once_with(
                db_session=session,
                organization_slug=None,
                service_id=None,
                conversation_target="instance-conversation-target",
                case_id=post_flow_instance.case.id,
                create_all_resources=False
            )

def test_signal_instance_create_flow_use_signal_attributes(session, signal, case_severity, case_priority, user, services, signal_instance,
                                                                              case_type, case):
    """
    If the signal instance does not specify a conversation target or on-call service, use the signal's configurations
    before the case type's configurations.
    """
    from dispatch.signal.flows import signal_instance_create_flow
    from dispatch.service import flows as service_flows
    from dispatch.case import service as case_service

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    service_0, service_1 = services
    service_0.project_id = signal.project_id
    service_1.project_id = signal.project_id

    signal_instance.signal.oncall_service = service_0
    signal_instance.signal.conversation_target = "signal-conversation-target"
    case_type.oncall_service = service_1
    case_type.conversation_target = "case-type-conversation-target"
    signal_instance.signal.case_type = case_type

    with mock.patch.object(service_flows, "resolve_oncall") as mock_resolve_oncall, \
         mock.patch.object(case_service, "create") as mock_case_create, \
         mock.patch("dispatch.case.flows.case_new_create_flow") as mock_case_new_create_flow:

        mock_resolve_oncall.side_effect = lambda service, db_session: "example@test.com" if service.id == service_0.id else None
        mock_case_create.return_value = case

        post_flow_instance = signal_instance_create_flow(
            signal_instance_id=signal_instance.id,
            db_session=session,
            current_user=user
        )
        case_in_arg = mock_case_create.call_args[1]['case_in']
        assert case_in_arg.assignee.individual.email == "example@test.com"
        if post_flow_instance is not None and hasattr(post_flow_instance, "case") and post_flow_instance.case is not None:
            mock_case_new_create_flow.assert_called_once_with(
                db_session=session,
                organization_slug=None,
                service_id=None,
                conversation_target="signal-conversation-target",
                case_id=post_flow_instance.case.id,
                create_all_resources=False
            )


def test_signal_instance_create_flow_use_case_type_attributes(session, signal, case_severity, case_priority, user, service, case, signal_instance, case_type):
    """
    If the signal instance and the signal both do not specify conversation targets or on-call services, use the case type's configurations.
    """
    from dispatch.signal.flows import signal_instance_create_flow
    from dispatch.service import flows as service_flows
    from dispatch.case import service as case_service

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    case_type.oncall_service = service
    case_type.conversation_target = "case-type-conversation-target"
    signal_instance.signal.case_type = case_type

    with mock.patch.object(service_flows, "resolve_oncall") as mock_resolve_oncall, \
        mock.patch.object(case_service, "create") as mock_case_create, \
        mock.patch("dispatch.case.flows.case_new_create_flow") as mock_case_new_create_flow:
        mock_resolve_oncall.side_effect = lambda service, db_session: "example@test.com"
        mock_case_create.return_value = case

        post_flow_instance = signal_instance_create_flow(
            signal_instance_id=signal_instance.id,
            db_session=session,
            current_user=user
        )
        case_in_arg = mock_case_create.call_args[1]['case_in']
        assert case_in_arg.assignee.individual.email == "example@test.com"
        if post_flow_instance is not None and hasattr(post_flow_instance, "case") and post_flow_instance.case is not None:
            mock_case_new_create_flow.assert_called_once_with(
                db_session=session,
                organization_slug=None,
                service_id=None,
                conversation_target="case-type-conversation-target",
                case_id=post_flow_instance.case.id,
                create_all_resources=False
            )
