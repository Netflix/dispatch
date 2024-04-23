from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Optional
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


def get_oncall_email(client: APISession, service_id: str) -> str:
    """Fetches the oncall's email for a given service."""
    service = get_service(client=client, service_id=service_id)
    escalation_policy_id = service["escalation_policy"]["id"]
    escalation_policy = get_escalation_policy(
        client=client, escalation_policy_id=escalation_policy_id
    )

    # Iterate over all escalation rules and targets to find the oncall user
    for rule in escalation_policy["escalation_rules"]:
        for target in rule["targets"]:
            filter_name = f"{target['type'].split('_')[0]}_ids[]"
            filter_value = target["id"]

            oncalls = list(
                client.iter_all(
                    "oncalls",  # method
                    {
                        filter_name: [filter_value],
                        "escalation_policy_ids[]": [escalation_policy_id],
                    },  # params
                )
            )

            if oncalls:
                user_id = list(oncalls)[0]["user"]["id"]
                user = get_user(client=client, user_id=user_id)
                return user["email"]

    # If we reach this point, we couldn't find the oncall user
    raise Exception(
        f"No users could be found for this pagerduty escalation policy ({escalation_policy_id}). Is there a schedule associated???"
    )


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


def get_oncall_at_time(client: APISession, schedule_id: str, utctime: str) -> Optional[dict]:
    """Retrieves the email of the oncall person at the utc time given."""
    try:
        oncalls = list(
            client.iter_all(
                "oncalls",  # method
                {
                    "schedule_ids[]": schedule_id,
                    "since": utctime,
                    "until": utctime,
                },  # params
            )
        )
        if not oncalls:
            raise Exception(
                f"No users could be found for PagerDuty schedule id {schedule_id}. Is there a schedule associated with it?"
            )

        user_id = oncalls[0]["user"]["id"]
        user = get_user(client, user_id)
        user_email = user["email"]
        shift_end = oncalls[0]["end"]
        schedule_name = oncalls[0]["schedule"]["summary"]
        return {
            "email": user_email,
            "shift_end": shift_end,
            "schedule_name": schedule_name,
        }

    except PDHTTPError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND.value:
            message = f"Schedule with id {schedule_id} not found."
            log.error(message)
            raise PDNotFoundError(message) from e
        else:
            raise e
    except PDClientError as e:
        log.error(f"Non-transient network or client error: {e}")
        raise e


def oncall_shift_check(client: APISession, schedule_id: str, hour: int) -> Optional[dict]:
    """Determines whether the oncall person just went off shift and returns their email."""
    now = datetime.utcnow()
    # in case scheduler is late, replace hour with exact one for shift comparison
    now = now.replace(hour=hour, minute=0, second=0, microsecond=0)

    # compare oncall person scheduled 18 hours ago vs 2 hours from now
    previous_shift = (now - timedelta(hours=18)).isoformat(timespec="minutes") + "Z"
    next_shift = (now + timedelta(hours=2)).isoformat(timespec="minutes") + "Z"

    previous_oncall = get_oncall_at_time(
        client=client, schedule_id=schedule_id, utctime=previous_shift
    )
    next_oncall = get_oncall_at_time(client=client, schedule_id=schedule_id, utctime=next_shift)

    if previous_oncall["email"] != next_oncall["email"]:
        return previous_oncall


def get_next_oncall(client: APISession, schedule_id: str) -> Optional[str]:
    """Retrieves the email of the next oncall person. Assumes 12-hour shifts"""
    now = datetime.utcnow()

    next_shift = (now + timedelta(hours=13)).isoformat(timespec="minutes") + "Z"
    next_oncall = get_oncall_at_time(client=client, schedule_id=schedule_id, utctime=next_shift)

    return None if not next_oncall else next_oncall["email"]
