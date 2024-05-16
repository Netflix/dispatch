from dispatch.plugins.bases import SecondarySystemPlugin


MOCK_INCIDENT_PLUGIN_RESPONSE = {
    "incident": {
        "external_issue_reference": {
            "provider": "jira",
            "issue_name": "TEST-123",
        },
        "id": "0123456789",
        "reference": "INC-0001",
        "name": "Test incident name",
        "summary": "Test incident summary",
        "incident_status": {
            "category": "test_category",
            "id": "0123456789",
            "name": "Investigating",
            "description": "There was an incident.",
            "rank": 1,
            "created_at": "2023-01-31T23:27:05.395Z",
            "updated_at": "2023-12-12T13:11:38.926Z"
        },
        "call_url": "https://meet.google.com/aaa-aaaa-aaa",
        "slack_team_id": "T00000000",
        "slack_channel_id": "C00000000",
        "slack_channel_name": "inc-0001-channel-name-here",
        "created_at": "2024-05-15T00:02:54.369Z",
        "updated_at": "2024-05-15T00:03:26.103Z",
        "mode": "standard",
        "visibility": "public",
        "severity": {
            "id": "0123456789",
            "name": "SEV 1",
            "description": "Severity 1",
            "rank": 2,
            "created_at": "2023-01-31T23:27:05.389Z",
            "updated_at": "2023-10-31T12:55:21.234Z"
        },
        "incident_type": {
            "id": "0123456789",
            "name": "Default",
            "is_default": True,
            "description": "",
            "private_incidents_only": False,
            "created_at": "2023-01-31T23:27:05.93Z",
            "updated_at": "2023-01-31T23:27:05.93Z",
            "create_in_triage": "optional"
        },
        "incident_role_assignments": [
            {
                "role": {
                    "id": "0123456789",
                    "name": "Incident Commander",
                    "shortform": "commander",
                    "description": "The person currently coordinating the incident",
                    "role_type": "lead",
                    "required": False,
                    "created_at": "2023-01-31T23:27:05.923Z",
                    "updated_at": "2023-11-10T21:16:28.329Z"
                },
                "assignee": {
                    "id": "0123456789",
                    "name": "David Tester",
                    "email": "dtester@test.com",
                    "slack_user_id": "U000000000",
                    "role": "responder"
                }
            },
            {
                "role": {
                    "id": "0123456789",
                    "name": "Reporter",
                    "shortform": "",
                    "description": "The person who reported the incident",
                    "instructions": "",
                    "role_type": "reporter",
                    "required": False,
                    "created_at": "2023-01-31T23:27:05.929Z",
                    "updated_at": "2023-01-31T23:27:05.929Z"
                },
                "assignee": {
                    "id": "0123456789",
                    "name": "Will Tester",
                    "email": "wtester@test.com",
                    "slack_user_id": "U000000001",
                    "role": "responder"
                }
            }
        ],
        "permalink": "https://app.incident.io/incidents/0123456789"
    }
}


class TestSecondarySystemPlugin(SecondarySystemPlugin):
    title = "Dispatch Test Plugin - Secondary System"
    slug = "test-secondary-system"

    def get(self, incident_id, **kwargs):
        return
