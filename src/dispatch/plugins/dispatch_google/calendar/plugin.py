"""
.. module: dispatch.plugins.dispatch_google_calendar.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from datetime import datetime, timedelta
from typing import Any, List

from pytz import timezone

from dispatch.decorators import apply, counter, timer
from dispatch.plugins.bases import ConferencePlugin
from dispatch.plugins.dispatch_google.common import get_service

from .config import GOOGLE_CALENDAR_ROOM_EMAIL


def get_event(client: Any, event_id: str):
    """Fetches a calendar event."""
    return client.get(calendarId="primary", eventId=event_id).execute()


def remove_participant(client: Any, event_id: int, participant: str):
    """Remove participant from calendar event."""
    event = get_event(client, event_id)

    attendees = []
    for a in event["attendees"]:
        if a["email"] != participant:
            attendees.append(a)

    event["attendees"] = attendees
    return client.update(calendarId="primary", eventId=event_id, body=event).execute()


def add_participant(client: Any, event_id: int, participant: str):
    event = get_event(client, event_id)
    event["attendees"].append({"email": participant})
    return client.update(calendarId="primary", eventId=event_id, body=event).execute()


def delete_event(client, event_id: int):
    return client.delete(calendarId="primary", eventId=event_id).execute()


def create_event(
    client,
    name: str,
    description: str = None,
    title: str = None,
    participants: List[str] = [],
    start_time: str = None,
    duration: int = 60,
):
    if start_time:
        raw_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        start = timezone("America/Los_Angeles").localize(raw_dt).astimezone(timezone("Etc/UTC"))
    else:
        start = datetime.utcnow()

    end = start + timedelta(minutes=duration)

    participants.append(GOOGLE_CALENDAR_ROOM_EMAIL)
    participants = [{"email": x} for x in participants]

    body = {
        "description": description if description else f"Situation Room for {name}. Please join.",
        "summary": title if title else f"Situation Room for {name}",
        "attendees": participants,
        "conferenceData": {"conferenceSolution": "hangoutsMeet"},
        "conferenceDataVersion": 1,
        "start": {"dateTime": start.isoformat(), "timeZone": "Etc/UTC"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Etc/UTC"},
        "guestsCanModify": True,
    }

    return client.insert(calendarId="primary", body=body, sendUpdates="all").execute()


@apply(timer, exclude=["__init__"])
@apply(counter, exclude=["__init__"])
class GoogleCalendarConferencePlugin(ConferencePlugin):
    title = "Google Calendar - Conference"
    slug = "google-calendar-conference"
    description = "Uses google calendar to manage conference rooms/meets."

    author = "Kevin Glisson"
    author_url = "https://github.com/netflix/dispatch.git"

    def __init__(self):
        scopes = ["https://www.googleapis.com/auth/calendar"]
        self.client = get_service("calendar", "v3", scopes).events()

    def create(self, name: str, description: str, title: str, participants: List[str] = []):
        """Create a new event."""
        return create_event(self.client, name, description, title, participants)

    def delete(self, event_id: str):
        """Deletes an existing event."""
        return delete_event(self.client, event_id)

    def add_participant(self, event_id: str, participant: str):
        """Adds a new participant to event."""
        return add_participant(self.client, event_id, participant)

    def remove_participant(self, event_id: str, participant: str):
        """Removes a participant from event."""
        return remove_participant(self.client, event_id, participant)
