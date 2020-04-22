import requests
import json
from dispatch.exceptions import DispatchPluginException
from .config import OPSGENIE_API_KEY, OPSGENIE_TEAM


def get_auth():
    return {"Authorization": f"GenieKey {OPSGENIE_API_KEY}"}


def get_oncall() -> str:
    schedule_api = "https://api.opsgenie.com/v2/schedules"
    params = {"scheduleIdentifierType": "name", "flat": "true"}
    response = requests.get(
        f"{schedule_api}/{OPSGENIE_TEAM}/on-calls",
        headers=get_auth(),
        params=params
    )

    if response.status_code != 200:
        raise DispatchPluginException

    body = response.json().get("data")

    if not body:
        raise DispatchPluginException

    return body["onCallRecipients"][0]


def page_oncall(
    incident_title: str, incident_name: str, incident_description: str
) -> str:
    data = {
        "message": incident_title,
        "alias": incident_title + incident_name,
        "description": incident_description,
    }

    response = requests.post(
        "https://api.opsgenie.com/v2/alerts",
        headers={**get_auth(), "content-type": "application/json"},
        data=json.dumps(data)
    )
    if response.status_code != 202:
        raise DispatchPluginException

    return response.json().get("requestId")
