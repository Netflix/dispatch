from typing import Any

def test_configure():
    """Test that we can configure the plugin."""
    from dispatch.plugins.dispatch_slack.incident.interactive import (
        configure,
    )
    from easydict import EasyDict

    config = EasyDict(
        {
            "api_bot_token": "xoxb-12345",
            "socket_mode_app_token": "xapp-12345",
            "signing_secret": "test-123",
            "app_user_slug": "test",
            "ban_threads": True,
            "timeline_event_reaction": "stopwatch",
            "slack_command_tasks": "/dispatch-list-tasks",
            "slack_command_list_my_tasks": "/dispatch-list-my-tasks",
            "slack_command_list_participants": "/dispatch-list-participants",
            "slack_command_assign_role": "/dispatch-assign-role",
            "slack_command_update_incident": "/dispatch-update-incident",
            "slack_command_update_participant": "/dispatch-update-participant",
            "slack_command_engage_oncall": "/dispatch-engage-oncall",
            "slack_command_list_resource": "/dispatch-list-resources",
            "slack_command_report_incident": "/dispatch-report-incident",
            "slack_command_report_tactical": "/dispatch-report-tactical",
            "slack_command_report_executive": "/dispatch-report-executive",
            "slack_command_update_notifications_group": "/dispatch-notifications-group",
            "slack_command_add_timeline_event": "/dispatch-add-timeline-event",
            "slack_command_list_incidents": "/dispatch-list-incidents",
            "slack_command_run_workflow": "/dispatch-run-workflow",
            "slack_command_list_workflow": "/dispatch-list-workflows",
            "slack_command_list_tasks": "/dispatch-list-tasks",
            "slack_command_create_task": "/dispatch-create-task",
        }
    )

    configure(config)


def test_handle_tag_search_action(session, incident):
    from dispatch.plugins.dispatch_slack.incident.interactive import (
        handle_tag_search_action,
    )
    from slack_bolt import Ack

    bolt_context = {"subject": incident}
    payload = {"value": "payload"}

    handle_tag_search_action(ack=Ack(), payload=payload, context=bolt_context, db_session=session)


def test_handle_list_incidents_command(session, incident, mock_slack_client):
    """Test that we can handle the list incidents command."""
    from dispatch.plugins.dispatch_slack.incident.interactive import (
        handle_list_incidents_command,
    )
    from slack_bolt import Ack
    from dispatch.plugins.dispatch_slack.models import SubjectMetadata, IncidentSubjects

    subject = SubjectMetadata(
        type=IncidentSubjects.incident,
        id=str(incident.id),
        organization_slug=incident.project.slug,
        project_id=str(incident.project.id),
    )

    bolt_context = {"subject": subject, "db_session": session}
    body = {"trigger_id": "trigger_id"}
    payload = {"value": "payload"}

    handle_list_incidents_command(
        ack=Ack(),
        body=body,
        payload=payload,
        context=bolt_context,
        db_session=session,
        client=mock_slack_client,
    )
