import logging
from typing import List

from dispatch.plugins.bases import ConferencePlugin
from dispatch.plugins.dispatch_microsoft_teams import conference as teams_plugin
from .config import MicrosoftTeamsConfiguration
from .client import MSTeamsClient
from dispatch.decorators import apply, counter, timer


logger = logging.getLogger(__name__)


class MicrosoftTeamsConferencePlugin(ConferencePlugin):
    title = "Microsoft Teams Plugin - Conference Management"
    slug = "microsoft-teams-conference"
    description = "Uses MS Teams to manage conference meetings."
    version = teams_plugin.__version__

    author = "Cino Jose"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.configuration_schema = MicrosoftTeamsConfiguration

    @apply(counter, exclude=["__init__"])
    @apply(timer, exclude=["__init__"])
    def create(
        self, name: str, description: str = None, title: str = None, participants: List[str] = None
    ):
        try:
            client = MSTeamsClient(
                client_id=self.configuration.client_id,
                authority=self.configuration.authority,
                credential=self.configuration.secret.get_secret_value(),
                user_id=self.configuration.user_id,
                record_automatically=self.configuration.allow_auto_recording,
            )
            meeting_info = client.create_meeting(name)

            return {
                "weblink": meeting_info["joinWebUrl"],
                "id": meeting_info["id"],
                "challenge": "",
            }
        except Exception as e:
            logger.error(f"There was an error when attempting to create the meeting {e}")
