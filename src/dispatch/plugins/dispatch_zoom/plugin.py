"""
.. module: dispatch.plugins.dispatch_zoom.plugin
    :platform: Unix
    :copyright: (c) 2019 by HashiCorp Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Will Bengtson <wbengtson@hashicorp.com>
"""
import logging
import random
from typing import List

from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_zoom as zoom_plugin
from dispatch.plugins.bases import ConferencePlugin

from .config import ZOOM_API_USER_ID, ZOOM_API_KEY, ZOOM_API_SECRET
from .client import ZoomClient

log = logging.getLogger(__name__)


def gen_conference_challenge(length: int):
    """Generate a random challenge for Zoom."""
    if length > 10:
        length = 10
    field = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.sample(field, length))


def delete_meeting(client, event_id: int):
    return client.delete("/meetings/{}".format(event_id))


def create_meeting(
    client,
    name: str,
    description: str = None,
    title: str = None,
    duration: int = 60000,  # duration in mins ~6 weeks
):
    """Create a Zoom Meeting."""
    body = {
        "topic": title if title else f"Situation Room for {name}",
        "agenda": description if description else f"Situation Room for {name}. Please join.",
        "duration": duration,
        "password": gen_conference_challenge(8),
        "settings": {"join_before_host": True},
    }

    return client.post("/users/{}/meetings".format(ZOOM_API_USER_ID), data=body)


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class ZoomConferencePlugin(ConferencePlugin):
    title = "Zoom Plugin - Conference Management"
    slug = "zoom-conference"
    description = "Uses Zoom to manage conference meetings."
    version = zoom_plugin.__version__

    author = "HashiCorp"
    author_url = "https://github.com/netflix/dispatch.git"

    def create(
        self, name: str, description: str = None, title: str = None, participants: List[str] = []
    ):
        """Create a new event."""
        client = ZoomClient(ZOOM_API_KEY, str(ZOOM_API_SECRET))

        conference_response = create_meeting(client, name, description=description, title=title)

        conference_json = conference_response.json()

        return {
            "weblink": conference_json.get("join_url", "https://zoom.us"),
            "id": conference_json.get("id", "1"),
            "challenge": conference_json.get("password", "123"),
        }

    def delete(self, event_id: str):
        """Deletes an existing event."""
        client = ZoomClient(ZOOM_API_KEY, str(ZOOM_API_SECRET))
        delete_meeting(client, event_id)

    def add_participant(self, event_id: str, participant: str):
        """Adds a new participant to event."""
        return

    def remove_participant(self, event_id: str, participant: str):
        """Removes a participant from event."""
        return
