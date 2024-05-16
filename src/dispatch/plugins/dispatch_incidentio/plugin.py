"""
.. module: dispatch.plugins.dispatch_incidentio.plugin
    :platform: Unix
    :copyright: (c) 2024 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: David Whittaker <dwhittaker@netflix.com>
"""
import logging
import requests
from requests.auth import HTTPBasicAuth

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_incidentio as incidentio_plugin
from dispatch.plugins.bases import SecondarySystemPlugin
from dispatch.plugins.dispatch_incidentio.config import (
    IncidentIOConfiguration,
)

logger = logging.getLogger(__name__)


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class IncidentIOPlugin(SecondarySystemPlugin):
    title = "IncidentIO Plugin - Secondary Incident Management System"
    slug = "incident-io-plugin"
    description = "Provides a connector to incident.io to import incidents."
    version = incidentio_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = IncidentIOConfiguration

    def parse_response(self, response: dict) -> dict:
        """Parses the response."""
        incident = response["incident"]

        incident_details = {}
        incident_details["id"] = incident["reference"]
        incident_details["title"] = incident["name"]
        incident_details["description"] = incident.get("summary", "")
        incident_details["status"] = incident["incident_status"]["name"]
        incident_details["priority"] = incident["incident_status"]["rank"]
        incident_details["severity"] = incident["severity"]["name"]
        reporter = ""
        incident_commander = ""
        for participant in incident["incident_role_assignments"]:
            if participant["role"]["name"] == "Incident Commander":
                incident_commander = participant["assignee"]["email"]
            if participant["role"]["name"] == "Reporter":
                if participant.get("assignee", ""):
                    reporter = participant["assignee"]["email"]

        incident_details["reporter"] = reporter
        incident_details["incident_commander"] = incident_commander

        return incident_details

    def get(self, incident_id: str) -> dict:
        """Fetches incident details."""
        try:
            api_call_headers = {'Authorization': 'Bearer ' + self.configuration.api_key.get_secret_value()}
            response = requests.get(
                f"https://api.incident.io/v2/incidents/{incident_id}",
                headers=api_call_headers,
            )
            return self.parse_response(response.json())
        except Exception as e:
            logger.error(e)
            raise

        # return completion.choices[0].message
