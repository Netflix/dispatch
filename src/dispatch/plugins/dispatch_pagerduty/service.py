def get_oncall_email(client, service: dict) -> str:
    """Fetches the oncall's email for a given service."""
    escalation_policy_id = service["escalation_policy"]["id"]
    escalation_policy = client.rget(f"/escalation_policies/{escalation_policy_id}")
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
            },  # params
        )
    )

    if oncalls:
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
    client,
    from_email: str,
    service_id: str,
    incident_name: str,
    incident_title: str,
    incident_description: str,
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
    headers = {"from": from_email}
    incident = client.rpost("/incidents", json=data, headers=headers)

    return incident
