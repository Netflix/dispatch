from .config import PAGERDUTY_API_FROM_EMAIL


def get_oncall_email(client, service: dict) -> str:
    """Fetches the oncall's email for a given service."""
    escalation_policy_id = service["escalation_policy"]["id"]
    escalation_policy = client.rget(f"/escalation_policies/{escalation_policy_id}")
    filter_name = "{}_ids[]".format(
        escalation_policy["escalation_rules"][0]["targets"][0]["type"].split("_")[0]
    )
    filter_value = escalation_policy["escalation_rules"][0]["targets"][0]["id"]

    oncalls = list(
        client.iter_all(
            "oncalls",  # method
            {
                # "include[]": "users", # including users doesn't give us the contact details
                filter_name: [filter_value],
                "escalation_policy_ids[]": [escalation_policy_id],
            },  # params
        )
    )

    if len(oncalls):
        user_id = list(oncalls)[0]["user"]["id"]
    else:
        raise Exception(
            f"No users could be found for this pagerduty escalation policy ({escalation_policy_id}). Is there a schedule associated?"
        )
    user = client.rget(f"/users/{user_id}")

    return user["email"]


def get_oncall(client, service_id: str):
    """Gets the oncall for a given service id or name."""
    service = client.rget(f"/services/{service_id}")
    return get_oncall_email(client, service)


def page_oncall(
    client, service_id: str, incident_name: str, incident_title: str, incident_description: str
):
    """Pages the oncall for a given service id."""
    service = client.rget(f"/services/{service_id}")

    escalation_policy_id = service["escalation_policy"]["id"]

    data = {
        "type": "incident",
        "title": f"{incident_name} - {incident_title}",
        "service": {"id": service_id, "type": "service_reference"},
        "body": {"type": "incident_body", "details": incident_description},
        "escalation_policy": {"id": escalation_policy_id, "type": "escalation_policy_reference"},
    }
    headers = {"from": PAGERDUTY_API_FROM_EMAIL}
    incident = client.rpost("/incidents", json=data, headers=headers)

    return incident
