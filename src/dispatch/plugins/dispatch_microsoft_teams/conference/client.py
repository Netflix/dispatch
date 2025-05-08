import msal
import logging
import requests
import json
from typing import Any

logger = logging.getLogger(__name__)


class MSTeamsClient:
    def __init__(
        self,
        client_id: str,
        authority: str,
        credential: str,
        record_automatically: bool,
        user_id: str,
        scope="https://graph.microsoft.com/.default",
    ):
        """
        "authority": "https://login.microsoftonline.com/Enter_the_Tenant_Id_Here",
        "client_id": "Enter_the_Application_Id_Here",
        "secret": "Enter_the_Client_Secret_Here"

        Enter_the_Application_Id_Here - is the Application (client) ID for the application you registered.
        Enter_the_Tenant_Id_Here - replace this value with the Tenant Id or Tenant name (for example, contoso.microsoft.com)
        Enter_the_Client_Secret_Here - replace this value with the client secret created on step 1
        """
        self.client_id = client_id
        self.authority = authority
        self.client_credential = credential
        self.scope = scope
        self.record_automatically = record_automatically
        self.user_id = user_id

    def _do_authenticate(self) -> Any:
        app = msal.ConfidentialClientApplication(
            self.client_id, authority=self.authority, client_credential=self.client_credential
        )
        """
        Contains the scopes requested. For confidential clients, this should use the format
        similar to {Application ID URI}/.default to indicate that the scopes being requested
        are the ones statically defined in the app object set in the Azure portal
        (for Microsoft Graph, {Application ID URI} points to https://graph.microsoft.com).
        For custom web APIs, {Application ID URI} is defined under the Expose an API section
        in App registrations in the Azure portal.
        """
        result = None
        logger.info("Completed app initialization")
        result = app.acquire_token_silent([self.scope], account=None)
        logger.info(f"Masked Result is {result}")
        if not result:
            logger.info("No suitable token exists in cache. Let's get a new one from AAD.")
            result = app.acquire_token_for_client(scopes=self.scope)
        return result

    def create_meeting(self, incident: str) -> dict:
        result = self._do_authenticate()
        if "access_token" in result:
            # Calling graph using the access token
            data = {
                "subject": f"{incident}",
                "recordAutomatically": str(self.record_automatically).lower(),
                "joinMeetingIdSettings": {"isPasscodeRequired": "false"},
            }
            graph_data = requests.post(  # Use token to call downstream service
                url=f"https://graph.microsoft.com/v1.0/users/{self.user_id}/onlineMeetings",
                headers={"Authorization": "Bearer " + result["access_token"]},
                json=data,
            ).json()
            logger.info("Graph API call result: ")
            logger.info(json.dumps(graph_data, indent=2))
            return graph_data

        return {}
