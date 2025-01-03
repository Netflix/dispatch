from unittest import mock
from unittest.mock import MagicMock

import pytest

from dispatch.exceptions import DispatchException


def test_create_signal_instance(session, signal, case_severity, case_priority, user):
    from dispatch.signal.flows import create_signal_instance

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    instance_data = {"variant": signal.variant}

    assert create_signal_instance(
        db_session=session,
        project=signal.project,
        signal_instance_data=instance_data,
        current_user=user,
    )


def test_create_signal_instance_no_variant(session, signal, case_severity, case_priority, user):
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


def test_create_signal_instance_not_enabled(session, signal, case_severity, case_priority, user):
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

def test_create_signal_instance_custom_conversation_target(session, signal, case_severity, case_priority, user, case_type):
    from dispatch.signal.flows import create_signal_instance

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    instance_data = {"variant": signal.variant, "conversation_target": "instance-conversation-target"}
    signal.conversation_target = "signal-conversation-target"

    signal_instance = create_signal_instance(
        db_session=session,
        project=signal.project,
        signal_instance_data=instance_data,
        current_user=user,
    )
    assert signal_instance.conversation_target == 'instance-conversation-target'


def test_create_signal_instance_custom_oncall_service(session, signal, case_severity, case_priority, user, services):
    from dispatch.signal.flows import create_signal_instance

    case_priority.default = True
    case_priority.project_id = signal.project_id

    case_severity.default = True
    case_severity.project_id = signal.project_id

    service_0, service_1 = services
    service_0.project_id = signal.project_id
    service_1.project_id = signal.project_id

    signal.oncall_service = service_0
    instance_data = {"variant": signal.variant, "oncall_service": service_1}

    signal_instance = create_signal_instance(
        db_session=session,
        project=signal.project,
        signal_instance_data=instance_data,
        current_user=user,
    )
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
        mock_case_new_create_flow.assert_called_once_with(
            db_session=session,
            organization_slug=None,
            service_id=None,
            conversation_target="case-type-conversation-target",
            case_id=post_flow_instance.case.id,
            create_all_resources=False
        )
