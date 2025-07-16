import pytest
from unittest.mock import Mock, patch

from dispatch.ai.service import generate_read_in_summary, READ_IN_SUMMARY_CACHE_DURATION, generate_tactical_report
from dispatch.ai.models import ReadInSummary, ReadInSummaryResponse, TacticalReport, TacticalReportResponse
from dispatch.ai.enums import AIEventSource, AIEventDescription
from dispatch.plugins.dispatch_slack.models import IncidentSubjects, CaseSubjects
from dispatch.enums import EventType
from dispatch.types import Subject


class TestGenerateReadInSummary:
    """Test suite for generate_read_in_summary function."""

    @pytest.fixture
    def mock_subject(self):
        """Create a mock subject for testing."""
        subject = Mock(spec=Subject)
        subject.id = 123
        subject.name = "Test Incident"
        subject.type = IncidentSubjects.incident
        return subject

    @pytest.fixture
    def mock_project(self):
        """Create a mock project for testing."""
        project = Mock()
        project.id = 456
        return project

    @pytest.fixture
    def mock_conversation(self):
        """Create mock conversation data."""
        return [
            {"user": "user1", "text": "Alert received", "timestamp": "2024-01-01 10:00"},
            {"user": "user2", "text": "Investigating the issue", "timestamp": "2024-01-01 10:05"},
            {"user": "user1", "text": "Issue resolved", "timestamp": "2024-01-01 10:30"},
        ]

    @pytest.fixture
    def mock_read_in_summary(self):
        """Create a mock ReadInSummary object."""
        return ReadInSummary(
            timeline=["2024-01-01 10:00: Alert received", "2024-01-01 10:30: Issue resolved"],
            actions_taken=["Investigated the alert", "Applied fix"],
            current_status="Resolved",
            summary="Security alert was investigated and resolved successfully",
        )

    def test_generate_read_in_summary_success_incident(
        self, session, mock_subject, mock_project, mock_conversation, mock_read_in_summary
    ):
        """Test successful read-in summary generation for an incident."""
        with (
            patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event,
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.event_service.log_incident_event") as mock_log_event,
        ):

            # Mock no recent event (cache miss)
            mock_get_event.return_value = None

            # Mock AI plugin
            mock_ai_plugin = Mock()
            mock_ai_plugin.instance.configuration.chat_completion_model = "gpt-4"
            mock_ai_plugin.instance.chat_parse.return_value = mock_read_in_summary

            # Mock conversation plugin
            mock_conv_plugin = Mock()
            mock_conv_plugin.instance.get_conversation.return_value = mock_conversation

            # Configure plugin service to return our mocks
            def get_plugin_side_effect(db_session, plugin_type, project_id):
                if plugin_type == "artificial-intelligence":
                    return mock_ai_plugin
                elif plugin_type == "conversation":
                    return mock_conv_plugin
                return None

            mock_get_plugin.side_effect = get_plugin_side_effect

            # Call the function
            result = generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Assertions
            assert isinstance(result, ReadInSummaryResponse)
            assert result.summary is not None
            assert result.error_message is None
            assert result.summary.timeline == mock_read_in_summary.timeline
            assert result.summary.actions_taken == mock_read_in_summary.actions_taken
            assert result.summary.current_status == mock_read_in_summary.current_status
            assert result.summary.summary == mock_read_in_summary.summary

            # Verify event logging
            mock_log_event.assert_called_once_with(
                db_session=session,
                source=AIEventSource.dispatch_genai,
                description=AIEventDescription.read_in_summary_created.format(
                    participant_email="test@example.com"
                ),
                incident_id=mock_subject.id,
                details=mock_read_in_summary.dict(),
                type=EventType.other,
            )

    def test_generate_read_in_summary_success_case(
        self, session, mock_subject, mock_project, mock_conversation, mock_read_in_summary
    ):
        """Test successful read-in summary generation for a case."""
        # Change subject type to case
        mock_subject.type = CaseSubjects.case

        with (
            patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event,
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.event_service.log_case_event") as mock_log_event,
        ):

            # Mock no recent event (cache miss)
            mock_get_event.return_value = None

            # Mock AI plugin
            mock_ai_plugin = Mock()
            mock_ai_plugin.instance.configuration.chat_completion_model = "gpt-4"
            mock_ai_plugin.instance.chat_parse.return_value = mock_read_in_summary

            # Mock conversation plugin
            mock_conv_plugin = Mock()
            mock_conv_plugin.instance.get_conversation.return_value = mock_conversation

            # Configure plugin service to return our mocks
            def get_plugin_side_effect(db_session, plugin_type, project_id):
                if plugin_type == "artificial-intelligence":
                    return mock_ai_plugin
                elif plugin_type == "conversation":
                    return mock_conv_plugin
                return None

            mock_get_plugin.side_effect = get_plugin_side_effect

            # Call the function
            result = generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Assertions
            assert isinstance(result, ReadInSummaryResponse)
            assert result.summary is not None
            assert result.error_message is None

            # Verify case event logging
            mock_log_event.assert_called_once_with(
                db_session=session,
                source=AIEventSource.dispatch_genai,
                description=AIEventDescription.read_in_summary_created.format(
                    participant_email="test@example.com"
                ),
                case_id=mock_subject.id,
                details=mock_read_in_summary.dict(),
                type=EventType.other,
            )

    def test_generate_read_in_summary_cache_hit(
        self, session, mock_subject, mock_project, mock_read_in_summary
    ):
        """Test read-in summary generation with cache hit."""
        with (
            patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event,
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
        ):

            # Mock recent event (cache hit)
            mock_event = Mock()
            mock_event.id = 789
            mock_event.details = mock_read_in_summary.dict()
            mock_get_event.return_value = mock_event

            # Call the function
            result = generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Assertions
            assert isinstance(result, ReadInSummaryResponse)
            assert result.summary is not None
            assert result.error_message is None
            assert result.summary.timeline == mock_read_in_summary.timeline

            # Verify no plugins were called (cache hit)
            mock_get_plugin.assert_not_called()

    def test_generate_read_in_summary_cache_invalid_data(
        self, session, mock_subject, mock_project, mock_conversation, mock_read_in_summary
    ):
        """Test read-in summary generation with invalid cached data."""
        with (
            patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event,
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):

            # Mock recent event with invalid data
            mock_event = Mock()
            mock_event.id = 789
            mock_event.details = {"timeline": "not a list"}  # This will cause validation error
            mock_get_event.return_value = mock_event

            # Mock AI plugin
            mock_ai_plugin = Mock()
            mock_ai_plugin.instance.configuration.chat_completion_model = "gpt-4"
            mock_ai_plugin.instance.chat_parse.return_value = mock_read_in_summary

            # Mock conversation plugin
            mock_conv_plugin = Mock()
            mock_conv_plugin.instance.get_conversation.return_value = mock_conversation

            # Configure plugin service to return our mocks
            def get_plugin_side_effect(db_session, plugin_type, project_id):
                if plugin_type == "artificial-intelligence":
                    return mock_ai_plugin
                elif plugin_type == "conversation":
                    return mock_conv_plugin
                return None

            mock_get_plugin.side_effect = get_plugin_side_effect

            # Call the function
            generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Verify warning was logged
            assert mock_log.warning.called

    def test_generate_read_in_summary_no_ai_plugin(self, session, mock_subject, mock_project):
        """Test read-in summary generation when no AI plugin is available."""
        with (
            patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event,
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):

            # Mock no recent event
            mock_get_event.return_value = None

            # Mock no AI plugin
            mock_get_plugin.return_value = None

            # Call the function
            result = generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Assertions
            assert isinstance(result, ReadInSummaryResponse)
            assert result.summary is None
            assert result.error_message is not None
            assert "No artificial-intelligence plugin enabled" in result.error_message

            # Verify warning was logged
            mock_log.warning.assert_called()

    def test_generate_read_in_summary_no_conversation_plugin(
        self, session, mock_subject, mock_project
    ):
        """Test read-in summary generation when no conversation plugin is available."""
        with (
            patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event,
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):

            # Mock no recent event
            mock_get_event.return_value = None

            # Mock AI plugin but no conversation plugin
            mock_ai_plugin = Mock()
            mock_get_plugin.side_effect = lambda db_session, plugin_type, project_id: (
                mock_ai_plugin if plugin_type == "artificial-intelligence" else None
            )

            # Call the function
            result = generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Assertions
            assert isinstance(result, ReadInSummaryResponse)
            assert result.summary is None
            assert result.error_message is not None
            assert "No conversation plugin enabled" in result.error_message

            # Verify warning was logged
            mock_log.warning.assert_called()

    def test_generate_read_in_summary_no_conversation(self, session, mock_subject, mock_project):
        """Test read-in summary generation when no conversation is found."""
        with (
            patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event,
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):

            # Mock no recent event
            mock_get_event.return_value = None

            # Mock AI plugin
            mock_ai_plugin = Mock()
            mock_ai_plugin.instance.configuration.chat_completion_model = "gpt-4"

            # Mock conversation plugin that returns no conversation
            mock_conv_plugin = Mock()
            mock_conv_plugin.instance.get_conversation.return_value = None

            # Configure plugin service to return our mocks
            def get_plugin_side_effect(db_session, plugin_type, project_id):
                if plugin_type == "artificial-intelligence":
                    return mock_ai_plugin
                elif plugin_type == "conversation":
                    return mock_conv_plugin
                return None

            mock_get_plugin.side_effect = get_plugin_side_effect

            # Call the function
            result = generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Assertions
            assert isinstance(result, ReadInSummaryResponse)
            assert result.summary is None
            assert result.error_message is not None
            assert "No conversation found" in result.error_message

            # Verify warning was logged
            mock_log.warning.assert_called()

    def test_generate_read_in_summary_ai_error(
        self, session, mock_subject, mock_project, mock_conversation
    ):
        """Test read-in summary generation when AI plugin throws an error."""
        with (
            patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event,
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):

            # Mock no recent event
            mock_get_event.return_value = None

            # Mock AI plugin that throws an error
            mock_ai_plugin = Mock()
            mock_ai_plugin.instance.configuration.chat_completion_model = "gpt-4"
            mock_ai_plugin.instance.chat_parse.side_effect = Exception("AI service error")

            # Mock conversation plugin
            mock_conv_plugin = Mock()
            mock_conv_plugin.instance.get_conversation.return_value = mock_conversation

            # Configure plugin service to return our mocks
            def get_plugin_side_effect(db_session, plugin_type, project_id):
                if plugin_type == "artificial-intelligence":
                    return mock_ai_plugin
                elif plugin_type == "conversation":
                    return mock_conv_plugin
                return None

            mock_get_plugin.side_effect = get_plugin_side_effect

            # Call the function
            result = generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Assertions
            assert isinstance(result, ReadInSummaryResponse)
            assert result.summary is None
            assert result.error_message is not None
            assert "Error generating read-in summary" in result.error_message

            # Verify error was logged
            mock_log.exception.assert_called()

    def test_generate_read_in_summary_cache_duration_constant(self):
        """Test that the cache duration constant is set correctly."""
        assert READ_IN_SUMMARY_CACHE_DURATION == 120  # 2 minutes

    def test_generate_read_in_summary_event_query_incident(
        self, session, mock_subject, mock_project
    ):
        """Test that the correct event query is made for incidents."""
        with patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event:
            mock_get_event.return_value = None

            # Call the function
            generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Verify the correct query was made
            mock_get_event.assert_called_once_with(
                session, incident_id=mock_subject.id, max_age_seconds=READ_IN_SUMMARY_CACHE_DURATION
            )

    def test_generate_read_in_summary_event_query_case(self, session, mock_subject, mock_project):
        """Test that the correct event query is made for cases."""
        # Change subject type to case
        mock_subject.type = CaseSubjects.case

        with patch("dispatch.ai.service.event_service.get_recent_summary_event") as mock_get_event:
            mock_get_event.return_value = None

            # Call the function
            generate_read_in_summary(
                db_session=session,
                subject=mock_subject,
                project=mock_project,
                channel_id="test-channel",
                important_reaction=":white_check_mark:",
                participant_email="test@example.com",
            )

            # Verify the correct query was made
            mock_get_event.assert_called_once_with(
                session, case_id=mock_subject.id, max_age_seconds=READ_IN_SUMMARY_CACHE_DURATION
            )



class TestGenerateTacticalReport:
    """Test suite for generate_tactical_report function."""

    @pytest.fixture
    def mock_incident(self):
        incident = Mock()
        incident.id = 321
        incident.name = "Tactical Incident"
        incident.conversation = Mock()
        incident.conversation.channel_id = "tactical-channel"
        return incident

    @pytest.fixture
    def mock_project(self):
        project = Mock()
        project.id = 654
        return project

    @pytest.fixture
    def mock_conversation(self):
        return [
            {"user": "user1", "text": "Initial event", "timestamp": "2024-02-01 10:00"},
            {"user": "user2", "text": "Mitigation step", "timestamp": "2024-02-01 10:15"},
        ]

    @pytest.fixture
    def mock_tactical_report(self):
        return TacticalReport(
            conditions="These are the conditions",
            actions=["Action 1", "Action 2"],
            needs=["Need 1"]
        )

    def test_generate_tactical_report_success(
        self, session, mock_incident, mock_project, mock_conversation, mock_tactical_report
    ):
        """Test successful tactical report generation."""
        with (
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.event_service.log_incident_event") as mock_log_event,
        ):
            # Mock AI plugin
            mock_ai_plugin = Mock()
            mock_ai_plugin.instance.configuration.chat_completion_model = "gpt-4"
            mock_ai_plugin.instance.chat_parse.return_value = mock_tactical_report

            # Mock conversation plugin
            mock_conv_plugin = Mock()
            mock_conv_plugin.instance.get_conversation.return_value = mock_conversation

            # Configure plugin service to return our mocks
            def get_plugin_side_effect(db_session, plugin_type, project_id):
                if plugin_type == "artificial-intelligence":
                    return mock_ai_plugin
                elif plugin_type == "conversation":
                    return mock_conv_plugin
                return None

            mock_get_plugin.side_effect = get_plugin_side_effect

            # Call the function
            result = generate_tactical_report(
                db_session=session,
                incident=mock_incident,
                project=mock_project,
                important_reaction=":fire:",
            )

            # Assertions
            assert isinstance(result, TacticalReportResponse)
            assert result.tactical_report is not None
            assert result.error_message is None
            assert result.tactical_report.conditions == mock_tactical_report.conditions
            assert result.tactical_report.actions == mock_tactical_report.actions
            assert result.tactical_report.needs == mock_tactical_report.needs

            # Verify event logging
            mock_log_event.assert_called_once_with(
                db_session=session,
                source=AIEventSource.dispatch_genai,
                description=AIEventDescription.tactical_report_created.format(
                    incident_name=mock_incident.name
                ),
                incident_id=mock_incident.id,
                details=mock_tactical_report.dict(),
                type=EventType.other,
            )

    def test_generate_tactical_report_no_ai_plugin(self, session, mock_incident, mock_project):
        """Test tactical report generation when no AI plugin is available."""
        with (
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):
            # No AI plugin
            mock_get_plugin.side_effect = lambda db_session, plugin_type, project_id: (
                None if plugin_type == "artificial-intelligence" else Mock()
            )

            result = generate_tactical_report(
                db_session=session,
                incident=mock_incident,
                project=mock_project,
                important_reaction=":fire:",
            )
            print(type(result))
            assert isinstance(result, TacticalReportResponse)
            assert result.tactical_report is None
            assert result.error_message is not None
            assert "No artificial-intelligence plugin enabled" in result.error_message
            mock_log.warning.assert_called()

    def test_generate_tactical_report_no_conversation_plugin(
        self, session, mock_incident, mock_project
    ):
        """Test tactical report generation when no conversation plugin is available."""
        with (
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):
            # AI plugin present, no conversation plugin
            mock_ai_plugin = Mock()
            mock_get_plugin.side_effect = lambda db_session, plugin_type, project_id: (
                mock_ai_plugin if plugin_type == "artificial-intelligence" else None
            )

            result = generate_tactical_report(
                db_session=session,
                incident=mock_incident,
                project=mock_project,
                important_reaction=":fire:",
            )

            assert isinstance(result, TacticalReportResponse)
            assert result.tactical_report is None
            assert result.error_message is not None
            assert "No conversation plugin enabled" in result.error_message
            mock_log.warning.assert_called()

    def test_generate_tactical_report_no_conversation(
        self, session, mock_incident, mock_project
    ):
        """Test tactical report generation when no conversation is found."""
        with (
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):
            # Mock AI plugin
            mock_ai_plugin = Mock()
            # Mock conversation plugin that returns no conversation
            mock_conv_plugin = Mock()
            mock_conv_plugin.instance.get_conversation.return_value = None

            def get_plugin_side_effect(db_session, plugin_type, project_id):
                if plugin_type == "artificial-intelligence":
                    return mock_ai_plugin
                elif plugin_type == "conversation":
                    return mock_conv_plugin
                return None

            mock_get_plugin.side_effect = get_plugin_side_effect

            result = generate_tactical_report(
                db_session=session,
                incident=mock_incident,
                project=mock_project,
                important_reaction=":fire:",
            )

            assert isinstance(result, TacticalReportResponse)
            assert result.tactical_report is None
            assert result.error_message is not None
            assert "No conversation found" in result.error_message
            mock_log.warning.assert_called()

    def test_generate_tactical_report_ai_error(
        self, session, mock_incident, mock_project, mock_conversation
    ):
        """Test tactical report generation when AI plugin throws an error."""
        with (
            patch("dispatch.ai.service.plugin_service.get_active_instance") as mock_get_plugin,
            patch("dispatch.ai.service.log") as mock_log,
        ):
            # Mock AI plugin with error
            mock_ai_plugin = Mock()
            mock_ai_plugin.instance.configuration.chat_completion_model = "gpt-4"
            mock_ai_plugin.instance.chat_parse.side_effect = Exception("AI error")

            # Mock conversation plugin
            mock_conv_plugin = Mock()
            mock_conv_plugin.instance.get_conversation.return_value = mock_conversation

            def get_plugin_side_effect(db_session, plugin_type, project_id):
                if plugin_type == "artificial-intelligence":
                    return mock_ai_plugin
                elif plugin_type == "conversation":
                    return mock_conv_plugin
                return None

            mock_get_plugin.side_effect = get_plugin_side_effect

            result = generate_tactical_report(
                db_session=session,
                incident=mock_incident,
                project=mock_project,
                important_reaction=":fire:",
            )

            assert isinstance(result, TacticalReportResponse)
            assert result.tactical_report is None
            assert result.error_message is not None
            assert "Error generating tactical report" in result.error_message
            mock_log.exception.assert_called()
