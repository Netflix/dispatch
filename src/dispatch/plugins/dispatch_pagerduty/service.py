from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Literal
import logging

from pdpyras import APISession, PDHTTPError, PDClientError


class PDNotFoundError(Exception):
    """Raised when a PagerDuty object is not found."""


log = logging.getLogger(__file__)


def get_user(client: APISession, user_id: str) -> dict:
    """Gets an oncall user by id."""
    try:
        user = client.rget(f"/users/{user_id}")
    except PDHTTPError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND.value:
            message = f"User with id {user_id} not found."
            log.error(message)
            raise PDNotFoundError(message) from e
        else:
            raise e
    except PDClientError as e:
        log.error(f"Non-transient network or client error: {e}")
        raise e

    return user


def get_service(client: APISession, service_id: str) -> dict:
    """Gets an oncall service by id."""
    try:
        service = client.rget(f"/services/{service_id}")
    except PDHTTPError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND.value:
            message = f"Service with id {service_id} not found."
            log.error(message)
            raise PDNotFoundError(message) from e
        else:
            raise e
    except PDClientError as e:
        log.error(f"Non-transient network or client error: {e}")
        raise e

    return service


def get_escalation_policy(client: APISession, escalation_policy_id: str) -> dict:
    """Gets an escalation policy by id."""
    try:
        escalation_policy = client.rget(f"/escalation_policies/{escalation_policy_id}")
    except PDHTTPError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND.value:
            message = f"Escalation policy with id {escalation_policy_id} not found."
            log.error(message)
            raise PDNotFoundError(message) from e
        else:
            raise e
    except PDClientError as e:
        log.error(f"Non-transient network or client error: {e}")
        raise e

    return escalation_policy


def create_incident(client: APISession, headers: dict, data: dict) -> dict:
    """Creates an incident and pages the oncall person."""
    try:
        incident = client.rpost("/incidents", headers=headers, json=data)
    except PDClientError as e:
        log.error(
            f"Error creating incident for service id {data['service']['id']} and escalation_policy id {data['escalation_policy']['id']}: {e}."
        )

    return incident


def get_oncall_info(client: APISession, service: dict, type: Literal["current", "next"]) -> dict:
    """Gets the current or next oncall info given a service."""
    escalation_policy_id = service["escalation_policy"]["id"]
    escalation_policy = get_escalation_policy(client, escalation_policy_id)

    filter_name = (
        f"{escalation_policy['escalation_rules'][0]['targets'][0]['type'].split('_')[0]}_ids[]"
    )
    filter_value = escalation_policy["escalation_rules"][0]["targets"][0]["id"]

    oncalls = list(
        client.iter_all(
            "oncalls",  # method
            {
                filter_name: [filter_value],
                "escalation_policy_ids[]": [escalation_policy_id],
                "until": datetime.utcnow() + timedelta(hours=6),
            },  # params
        )
    )

    if not oncalls:
        raise Exception(
            f"No users could be found for this PagerDuty escalation policy ({escalation_policy_id}). Is there a schedule associated to it?"
        )

    oncalls_info = []
    for oncall in oncalls:
        user_id = oncall["user"]["id"]
        user = get_user(client, user_id)
        oncalls_info.append(
            {
                "name": user["name"],
                "email": user["email"],
                # "time_zone": user["time_zone"],
                "start": oncall["start"],
                "end": oncall["end"],
            }
        )

    if len(oncalls_info) == 1:
        return oncalls_info[0]
    else:
        if type == "current":
            return oncalls_info[0]

        if type == "next":
            return oncalls_info[-1]


def get_oncall(client: APISession, service_id: str, type: Literal["current", "next"]) -> str:
    """Gets the oncall for a given service id or name."""
    service = get_service(client, service_id)
    return get_oncall_info(client, service, type)


def page_oncall(
    client: APISession,
    from_email: str,
    service_id: str,
    incident_name: str,
    incident_title: str,
    incident_description: str,
) -> dict:
    """Pages the oncall for a given service id."""
    service = get_service(client, service_id)
    escalation_policy_id = service["escalation_policy"]["id"]

    headers = {"from": from_email}
    data = {
        "type": "incident",
        "title": f"{incident_name} - {incident_title}",
        "service": {"id": service_id, "type": "service_reference"},
        "body": {"type": "incident_body", "details": incident_description},
        "escalation_policy": {"id": escalation_policy_id, "type": "escalation_policy_reference"},
    }

    return create_incident(client, headers, data)
