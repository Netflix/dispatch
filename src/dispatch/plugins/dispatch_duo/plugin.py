"""
.. module: dispatch.plugins.dispatch_duo.plugin
    :platform: Unix
    :copyright: (c) 2023 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Will Sheldon <wshel@netflix.com>
"""
import logging
from typing import NewType

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import MultiFactorAuthenticationPlugin
from dispatch.plugins.dispatch_duo.enums import PushResponseResult
from dispatch.plugins.dispatch_duo import service as duo_service
from dispatch.plugins.dispatch_duo.config import DuoConfiguration
from . import __version__

log = logging.getLogger(__name__)


DuoAuthResponse = NewType(
    "DuoAuthResponse",
    dict[
        str,
        dict[str, str] | str,
    ],
)


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class DuoMfaPlugin(MultiFactorAuthenticationPlugin):
    title = "Duo Plugin - Multi Factor Authentication"
    slug = "duo-auth-mfa"
    description = "Uses Duo to validate user actions with multi-factor authentication."
    version = __version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = DuoConfiguration

    def send_push_notification(
        self,
        username: str,
        type: str,
        device: str = "auto",
    ) -> DuoAuthResponse:
        """Create a new push notification for authentication.

        This function sends a push notification to a Duo-enabled device for multi-factor authentication.

        Args:
            username (str): The unique identifier for the user, commonly specified by your application during user
                creation (e.g. wshel@netflix.com). This value may also represent a username alias assigned to a user (e.g. wshel).

            type (str): A string that is displayed in the Duo Mobile app push notification and UI. The notification text
                changes to "Verify request" and shows your customized string followed by a colon and the application's name,
                and the request details screen also shows your customized string and the application's name.

            device (str, optional): The ID of the device. This device must have the "push" capability. Defaults to "auto"
                to use the first of the user's devices with the "push" capability.

        Returns:
            DuoAuthResponse: The response from the Duo API. A successful response would appear as:
                {"response": {"result": "allow", "status": "allow", "status_msg": "Success. Logging you in..."}, "stat": "OK"}

        Example:
            >>> plugin = DuoMfaPlugin()
            >>> result = plugin.send_push_notification(username='wshel@netflix.com', type='Login Request')
            >>> result
            {'response': {'result': 'allow', 'status': 'allow', 'status_msg': 'Success. Logging you in...'}, 'stat': 'OK'}

        Notes:
            For more information, see https://duo.com/docs/authapi#/auth
        """
        duo_client = duo_service.create_duo_auth_client(self.configuration)
        try:
            response = duo_client.auth(factor="push", username=username, device=device, type=type)
        except RuntimeError as e:
            if "Invalid request parameters (username)" in str(e):
                username, _ = username.split("@")

                try:
                    response = duo_client.auth(
                        factor="push", username=username, device=device, type=type
                    )
                except RuntimeError as e:
                    if "Invalid request parameters (username)" in str(e):
                        log.warning(
                            f"Sending push notification failed. Unable to find {username} in Duo"
                        )
                        return PushResponseResult.user_not_found

        if response.get("result") == PushResponseResult.allow:
            return PushResponseResult.allow

        if response.get("status") == PushResponseResult.timeout:
            return PushResponseResult.timeout

        return response
