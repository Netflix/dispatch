import json
import requests

from dispatch.exceptions import DispatchPluginException


def get_auth(api_key: str) -> dict:
    return {"Authorization": f"GenieKey {api_key.get_secret_value()}"}


def get_oncall(api_key: str, team_id: str) -> str:
    schedule_api = "https://api.opsgenie.com/v2/schedules"
    response = requests.get(
        f"{schedule_api}/{team_id}/on-calls",
        headers=get_auth(api_key),
    )

    if response.status_code != 200:
        raise DispatchPluginException(response.text)

    body = response.json().get("data")

    if not body:
        raise DispatchPluginException

    return body["onCallParticipants"][0].get("name")


def page_oncall(
    api_key: str,
    service_id: str,
    incident_name: str,
    incident_title: str,
    incident_description: str,
) -> str:
    data = {
        "message": incident_title,
        "alias": f"{incident_name}-{incident_title}",
        "description": incident_description,
        "responders": [{"id": service_id, "type": "schedule"}],
    }

    response = requests.post(
        "https://api.opsgenie.com/v2/alerts",
        headers={**get_auth(api_key), "content-type": "application/json"},
        data=json.dumps(data),
    )
    if response.status_code != 202:
        raise DispatchPluginException

    return response.json().get("requestId")
