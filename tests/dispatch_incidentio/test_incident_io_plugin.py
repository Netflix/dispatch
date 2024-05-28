# tests secondary system plugin


def test_get_incident():
    """Tests the get_all function."""
    from dispatch.plugins.dispatch_incidentio.plugin import IncidentIOPlugin
    from dispatch.plugins.dispatch_test.incident_management import MOCK_INCIDENT_PLUGIN_RESPONSE

    plugin = IncidentIOPlugin()
    incident = plugin.parse_response(MOCK_INCIDENT_PLUGIN_RESPONSE)
    assert (
        incident["id"] == "INC-0001"
        and incident["title"] == "Test incident name"
        and incident["description"] == "Test incident summary"
        and incident["status"] == "Investigating"
        and incident["priority"] == 1
        and incident["severity"] == "SEV 1"
        and incident["reporter"] == "wtester@test.com"
        and incident["incident_commander"] == "dtester@test.com"
    )
