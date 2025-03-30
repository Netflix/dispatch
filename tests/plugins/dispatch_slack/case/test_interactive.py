from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from dispatch.auth.models import MfaChallengeStatus
from dispatch.plugins.dispatch_slack.case.interactive import (
    handle_snooze_submission_event,
    get_user_id_from_oncall_service,
    post_snooze_message,
)


class TestHandleSnoozeSubmissionEvent:
    @pytest.fixture
    def mock_ack(self):
        return MagicMock()

    @pytest.fixture
    def mock_body(self):
        return {"view": {"id": "view_id"}}

    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_context(self):
        relative_date_picker = MagicMock()
        relative_date_picker.value = "1 day, 0:00:00"

        extension_checkbox_item = MagicMock()
        extension_checkbox_item.value = "Yes"

        entity_select_item = MagicMock()
        entity_select_item.value = "789"

        return {
            "subject": MagicMock(
                id="123",
                project_id="456",
                channel_id="C123",
                thread_id="T123",
                form_data={
                    "title-input": "Test Snooze",
                    "description-input": "Test Description",
                    "relative-date-picker-input": relative_date_picker,
                    "extension-request-checkbox": [extension_checkbox_item],
                    "entity-select": [entity_select_item],
                },
                dict=MagicMock(return_value={}),
            )
        }

    @pytest.fixture
    def mock_db_session(self):
        return MagicMock()

    @pytest.fixture
    def mock_user(self):
        return MagicMock(email="test@example.com")

    @patch("dispatch.plugins.dispatch_slack.case.interactive.plugin_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.signal_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.post_snooze_message")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.send_success_modal")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.project_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.SignalFilterCreate")
    def test_handle_snooze_submission_event_no_mfa(
        self,
        mock_signal_filter_create,
        mock_project_service,
        mock_send_success_modal,
        mock_post_snooze_message,
        mock_signal_service,
        mock_plugin_service,
        mock_ack,
        mock_body,
        mock_client,
        mock_context,
        mock_db_session,
        mock_user,
    ):
        # Setup
        mock_plugin_service.get_active_instance.return_value = None
        mock_signal = MagicMock()
        mock_signal_service.get.return_value = mock_signal
        mock_new_filter = MagicMock()
        mock_signal_service.create_signal_filter.return_value = mock_new_filter

        # Mock the project
        mock_project = MagicMock()
        mock_project.id = "456"
        mock_project.name = "Test Project"
        mock_project.organization.slug = "test-org"
        mock_project_service.get.return_value = mock_project

        # Mock the SignalFilterCreate to avoid validation errors
        mock_filter_instance = MagicMock()
        mock_signal_filter_create.return_value = mock_filter_instance

        # Execute
        handle_snooze_submission_event(
            ack=mock_ack,
            body=mock_body,
            client=mock_client,
            context=mock_context,
            db_session=mock_db_session,
            user=mock_user,
        )

        # Assert
        mock_signal_service.create_signal_filter.assert_called_once()
        # The implementation calls get twice, so we don't assert the exact number of calls
        assert mock_signal_service.get.call_count >= 1
        mock_post_snooze_message.assert_called_once()
        mock_send_success_modal.assert_called_once()

    @patch("dispatch.plugins.dispatch_slack.case.interactive.plugin_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.signal_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.post_snooze_message")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.send_success_modal")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.project_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.SignalFilterCreate")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.ack_mfa_required_submission_event")
    def test_handle_snooze_submission_event_with_mfa_approved(
        self,
        mock_ack_mfa_required,
        mock_signal_filter_create,
        mock_project_service,
        mock_send_success_modal,
        mock_post_snooze_message,
        mock_signal_service,
        mock_plugin_service,
        mock_ack,
        mock_body,
        mock_client,
        mock_context,
        mock_db_session,
        mock_user,
    ):
        # Setup
        mock_mfa_plugin = MagicMock()
        mock_mfa_plugin.instance.create_mfa_challenge.return_value = (MagicMock(), "challenge_url")
        mock_mfa_plugin.instance.wait_for_challenge.return_value = MfaChallengeStatus.APPROVED
        mock_plugin_service.get_active_instance.return_value = mock_mfa_plugin

        mock_signal = MagicMock()
        mock_signal_service.get.return_value = mock_signal
        mock_new_filter = MagicMock()
        mock_signal_service.create_signal_filter.return_value = mock_new_filter

        # Mock the project
        mock_project = MagicMock()
        mock_project.id = "456"
        mock_project.name = "Test Project"
        mock_project.organization.slug = "test-org"
        mock_project_service.get.return_value = mock_project

        # Mock the SignalFilterCreate to avoid validation errors
        mock_filter_instance = MagicMock()
        mock_signal_filter_create.return_value = mock_filter_instance

        # Execute
        handle_snooze_submission_event(
            ack=mock_ack,
            body=mock_body,
            client=mock_client,
            context=mock_context,
            db_session=mock_db_session,
            user=mock_user,
        )

        # Assert
        mock_mfa_plugin.instance.create_mfa_challenge.assert_called_once()
        mock_mfa_plugin.instance.wait_for_challenge.assert_called_once()
        mock_signal_service.create_signal_filter.assert_called_once()
        # The implementation calls get twice, so we don't assert the exact number of calls
        assert mock_signal_service.get.call_count >= 1
        mock_post_snooze_message.assert_called_once()
        mock_send_success_modal.assert_called_once()
        assert mock_user.last_mfa_time is not None

    @patch("dispatch.plugins.dispatch_slack.case.interactive.plugin_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.signal_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.post_snooze_message")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.send_success_modal")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.ack_mfa_required_submission_event")
    def test_handle_snooze_submission_event_with_mfa_denied(
        self,
        mock_ack_mfa,
        mock_send_success_modal,
        mock_post_snooze_message,
        mock_signal_service,
        mock_plugin_service,
        mock_ack,
        mock_body,
        mock_client,
        mock_context,
        mock_db_session,
        mock_user,
    ):
        # Setup
        mock_mfa_plugin = MagicMock()
        mock_mfa_plugin.instance.create_mfa_challenge.return_value = (MagicMock(), "challenge_url")
        mock_mfa_plugin.instance.wait_for_challenge.return_value = MfaChallengeStatus.DENIED
        mock_plugin_service.get_active_instance.return_value = mock_mfa_plugin

        # Execute
        handle_snooze_submission_event(
            ack=mock_ack,
            body=mock_body,
            client=mock_client,
            context=mock_context,
            db_session=mock_db_session,
            user=mock_user,
        )

        # Assert
        mock_mfa_plugin.instance.create_mfa_challenge.assert_called_once()
        mock_mfa_plugin.instance.wait_for_challenge.assert_called_once()
        mock_signal_service.create_signal_filter.assert_not_called()
        mock_signal_service.get.assert_not_called()
        mock_post_snooze_message.assert_not_called()
        mock_client.views_update.assert_called_once()


class TestGetUserIdFromOncallService:
    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_db_session(self):
        return MagicMock()

    @patch("dispatch.plugins.dispatch_slack.case.interactive.service_flows")
    def test_get_user_id_from_oncall_service_none_service(
        self, mock_service_flows, mock_client, mock_db_session
    ):
        # Setup
        oncall_service = None

        # Execute
        result = get_user_id_from_oncall_service(
            client=mock_client, db_session=mock_db_session, oncall_service=oncall_service
        )

        # Assert
        assert result is None
        mock_service_flows.resolve_oncall.assert_not_called()
        mock_client.users_lookupByEmail.assert_not_called()

    @patch("dispatch.plugins.dispatch_slack.case.interactive.service_flows")
    def test_get_user_id_from_oncall_service_no_email(
        self, mock_service_flows, mock_client, mock_db_session
    ):
        # Setup
        oncall_service = MagicMock()
        mock_service_flows.resolve_oncall.return_value = None

        # Execute
        result = get_user_id_from_oncall_service(
            client=mock_client, db_session=mock_db_session, oncall_service=oncall_service
        )

        # Assert
        assert result is None
        mock_service_flows.resolve_oncall.assert_called_once_with(
            service=oncall_service, db_session=mock_db_session
        )
        mock_client.users_lookupByEmail.assert_not_called()

    @patch("dispatch.plugins.dispatch_slack.case.interactive.service_flows")
    def test_get_user_id_from_oncall_service_success(
        self, mock_service_flows, mock_client, mock_db_session
    ):
        # Setup
        oncall_service = MagicMock()
        mock_service_flows.resolve_oncall.return_value = "oncall@example.com"
        mock_client.users_lookupByEmail.return_value = {"user": {"id": "U123"}}

        # Execute
        result = get_user_id_from_oncall_service(
            client=mock_client, db_session=mock_db_session, oncall_service=oncall_service
        )

        # Assert
        assert result == "U123"
        mock_service_flows.resolve_oncall.assert_called_once_with(
            service=oncall_service, db_session=mock_db_session
        )
        mock_client.users_lookupByEmail.assert_called_once_with(email="oncall@example.com")

    @patch("dispatch.plugins.dispatch_slack.case.interactive.service_flows")
    def test_get_user_id_from_oncall_service_slack_error(
        self, mock_service_flows, mock_client, mock_db_session
    ):
        # Setup
        oncall_service = MagicMock()
        mock_service_flows.resolve_oncall.return_value = "oncall@example.com"
        mock_client.users_lookupByEmail.side_effect = SlackApiError("Error", {"error": "not_found"})

        # Execute
        result = get_user_id_from_oncall_service(
            client=mock_client, db_session=mock_db_session, oncall_service=oncall_service
        )

        # Assert
        assert result is None
        mock_service_flows.resolve_oncall.assert_called_once_with(
            service=oncall_service, db_session=mock_db_session
        )
        mock_client.users_lookupByEmail.assert_called_once_with(email="oncall@example.com")


class TestPostSnoozeMessage:
    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_db_session(self):
        return MagicMock()

    @pytest.fixture
    def mock_user(self):
        return MagicMock(email="test@example.com")

    @pytest.fixture
    def mock_signal(self):
        return MagicMock(name="Test Signal")

    @pytest.fixture
    def mock_new_filter(self):
        return MagicMock(
            name="Test Filter",
            description="Test Description",
            expiration=datetime.now(tz=timezone.utc) + timedelta(days=1),
            expression=[],
        )

    def test_post_snooze_message_no_entities(
        self, mock_client, mock_db_session, mock_user, mock_signal, mock_new_filter
    ):
        # Setup
        channel = "C123"
        thread_ts = "T123"
        extension_requested = False
        oncall_service = None

        # Execute
        post_snooze_message(
            client=mock_client,
            channel=channel,
            user=mock_user,
            signal=mock_signal,
            db_session=mock_db_session,
            new_filter=mock_new_filter,
            thread_ts=thread_ts,
            extension_requested=extension_requested,
            oncall_service=oncall_service,
        )

        # Assert
        mock_client.chat_postMessage.assert_called_once()
        args, kwargs = mock_client.chat_postMessage.call_args
        assert kwargs["channel"] == channel
        assert kwargs["thread_ts"] == thread_ts
        assert "New Signal Snooze Added" in kwargs["text"]
        assert "Entities: All" in kwargs["text"]
        assert "Extension Requested" not in kwargs["text"]

    @patch("dispatch.plugins.dispatch_slack.case.interactive.entity_service")
    @patch("dispatch.plugins.dispatch_slack.case.interactive.get_user_id_from_oncall_service")
    def test_post_snooze_message_with_entities_and_extension(
        self,
        mock_get_user_id,
        mock_entity_service,
        mock_client,
        mock_db_session,
        mock_user,
        mock_signal,
        mock_new_filter,
    ):
        # Setup
        channel = "C123"
        thread_ts = "T123"
        extension_requested = True
        oncall_service = MagicMock()

        # Setup entity expression
        mock_new_filter.expression = [
            {
                "or": [
                    {"model": "Entity", "field": "id", "value": "123"},
                    {"model": "Entity", "field": "id", "value": "456"},
                ]
            }
        ]

        # Setup entities
        mock_entity1 = MagicMock(id=123, value="entity1")
        mock_entity2 = MagicMock(id=456, value="entity2")
        mock_entity_service.get.side_effect = [mock_entity1, mock_entity2]

        # Setup oncall user
        mock_get_user_id.return_value = "U123"

        # Execute
        post_snooze_message(
            client=mock_client,
            channel=channel,
            user=mock_user,
            signal=mock_signal,
            db_session=mock_db_session,
            new_filter=mock_new_filter,
            thread_ts=thread_ts,
            extension_requested=extension_requested,
            oncall_service=oncall_service,
        )

        # Assert
        mock_client.chat_postMessage.assert_called_once()
        args, kwargs = mock_client.chat_postMessage.call_args
        assert kwargs["channel"] == channel
        assert kwargs["thread_ts"] == thread_ts
        assert "New Signal Snooze Added" in kwargs["text"]
        assert "Entities: entity1 (123), entity2 (456)" in kwargs["text"]
        assert "Extension Requested" in kwargs["text"]
        assert "notifying oncall: <@U123>" in kwargs["text"]
