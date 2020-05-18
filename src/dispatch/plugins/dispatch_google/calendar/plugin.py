"""
.. module: dispatch.plugins.dispatch_google_calendar.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, List

from googleapiclient.errors import HttpError
from pytz import timezone
from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import ConferencePlugin
from dispatch.plugins.dispatch_google import calendar as google_calendar_plugin
from dispatch.plugins.dispatch_google.common import get_service


log = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(TryAgain),
    wait=wait_exponential(multiplier=1, min=2, max=5),
)
def make_call(client: Any, func: Any, delay: int = None, propagate_errors: bool = False, **kwargs):
    """Make an google client api call."""
    try:
        data = getattr(client, func)(**kwargs).execute()

        if delay:
            time.sleep(delay)

        return data
    except HttpError:
        raise TryAgain


def get_event(client: Any, event_id: str):
    """Fetches a calendar event."""
    return make_call(client.events(), "get", calendarId="primary", eventId=event_id)


def remove_participant(client: Any, event_id: int, participant: str):
    """Remove participant from calendar event."""
    event = get_event(client, event_id)

    attendees = []
    for a in event["attendees"]:
        if a["email"] != participant:
            attendees.append(a)

    event["attendees"] = attendees
    return make_call(client.events(), "update", calendarId="primary", eventId=event_id, body=event)


def add_participant(client: Any, event_id: int, participant: str):
    event = get_event(client, event_id)
    event["attendees"].append({"email": participant})
    return make_call(client.events(), "update", calendarId="primary", eventId=event_id, body=event)


def delete_event(client, event_id: int):
    return make_call(client.events(), "delete", calendarId="primary", eventId=event_id)


def create_event(
    client,
    name: str,
    description: str = None,
    title: str = None,
    participants: List[str] = [],
    start_time: str = None,
    duration: int = 60000,  # duration in mins ~6 weeks
):
    participants = [{"email": x} for x in participants]

    request_id = str(uuid.uuid4())
    body = {
        "description": description if description else f"Situation Room for {name}. Please join.",
        "summary": title if title else f"Situation Room for {name}",
        "attendees": participants,
        "conferenceData": {
            "createRequest": {
                "requestId": request_id,
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
        "guestsCanModify": True,
    }

    if start_time:
        raw_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        start = timezone("America/Los_Angeles").localize(raw_dt).astimezone(timezone("Etc/UTC"))
    else:
        start = datetime.utcnow()

    end = start + timedelta(minutes=duration)
    body.update(
        {
            "start": {"date": start.isoformat().split("T")[0], "timeZone": "Etc/UTC"},
            "end": {"date": end.isoformat().split("T")[0], "timeZone": "Etc/UTC"},
        }
    )

    # TODO sometimes google is slow with the meeting invite, we should poll/wait
    return make_call(
        client.events(), "insert", calendarId="primary", body=body, conferenceDataVersion=1
    )


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleCalendarConferencePlugin(ConferencePlugin):
    title = "Google Calendar Plugin - Conference Management"
    slug = "google-calendar-conference"
    description = "Uses Google calendar to manage conference rooms/meets."
    version = google_calendar_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        self.scopes = ["https://www.googleapis.com/auth/calendar"]

    def create(
        self, name: str, description: str = None, title: str = None, participants: List[str] = []
    ):
        """Create a new event."""
        client = get_service("calendar", "v3", self.scopes)
        conference = create_event(
            client, name, description=description, participants=participants, title=title
        )

        meet_url = ""
        for entry_point in conference["conferenceData"]["entryPoints"]:
            if entry_point["entryPointType"] == "video":
                meet_url = entry_point["uri"]

        return {"weblink": meet_url, "id": conference["id"], "challenge": ""}

    def delete(self, event_id: str):
        """Deletes an existing event."""
        client = get_service("calendar", "v3", self.scopes)
        return delete_event(client, event_id)

    def add_participant(self, event_id: str, participant: str):
        """Adds a new participant to event."""
        client = get_service("calendar", "v3", self.scopes)
        return add_participant(client, event_id, participant)

    def remove_participant(self, event_id: str, participant: str):
        """Removes a participant from event."""
        client = get_service("calendar", "v3", self.scopes)
        return remove_participant(client, event_id, participant)
