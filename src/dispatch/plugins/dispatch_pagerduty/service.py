from datetime import datetime, timedelta


def get_oncall_email(client, service: dict) -> str:
    """Fetches the oncall's email for a given service."""
    escalation_policy_id = service["escalation_policy"]["id"]
    oncalls = get_oncalls_from_escalation_policy(escalation_policy_id)

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


def get_oncalls_from_escalation_policy(client, escalation_policy_id: str):
    """Gets the oncalls for a given escalation policy id or name."""
    escalation_policy = client.rget(f"/escalation_policies/{escalation_policy_id}")
    filter_name = (
        f"{escalation_policy['escalation_rules'][0]['targets'][0]['type'].split('_')[0]}_ids[]"
    )
    filter_value = escalation_policy["escalation_rules"][0]["targets"][0]["id"]

    return list(
        client.iter_all(
            "oncalls",  # method
            {
                filter_name: [filter_value],
                "escalation_policy_ids[]": [escalation_policy_id],
            },  # params
        )
    )


def get_oncall_schedule(client, service: dict, param={}) -> list[dict]:
    """Gets the oncall schedule."""
    escalation_policy_id = service["escalation_policy"]["id"]
    oncalls = get_oncalls_from_escalation_policy(escalation_policy_id)

    if oncalls:
        schedule_id = list(oncalls)[0]["schedule"]["id"]
    else:
        raise Exception(
            f"No schedule could be found for this pagerduty escalation policy ({escalation_policy_id})."
        )

    # Grabs the oncall schedule from the last 14 hours by default. Assumes the oncall shifts are at least
    # 12 hours long. The offset accounts for shift changes at the cutoff time.
    if not param:
        now = datetime.now()
        offset = 1
        param["until"] = now + timedelta(hours=offset)
        param["since"] = now - timedelta(hours=12 + offset)

    param["include[]"] = "schedule_layers"
    return client.rget(f"/schedules/{schedule_id}", param=param)


def send_shift_feedback_form_message(client, service_id: str, param={}):
    """Sends the oncall shift feedback form to the oncalls at the end of their shift.
    Args:
        service_id: ID of the PagerDuty service resource
        param: A dictionary containing the query parameters to be sent to the PagerDuty API.
               See https://developer.pagerduty.com/api-reference/165ad96a22ffd-get-a-service#Query-Parameters for more information.
    """
    service = client.rget(f"/services/{service_id}")
    schedule = get_oncall_schedule(client, service, param)

    # TODO: Identify if an override has ended their shift. The override layer does not identify which
    # schedule layer it is overriding. This layer could potentially go on indefinitely.
    if schedule["overrides_subschedule"]:
        unique_users = list(
            set(
                entry.user.id
                for entry in schedule["overrides_subschedule"]["rendered_schedule_entries"]
            )
        )
        for user in unique_users:
            # TODO: send_oncall_shift_feedback_message
            pass

    # Handle the normal layers
    for layer in schedule["schedule"]["schedule_layers"]:
        if layer["rendered_coverage_percentage"] == 0:
            continue

        # Checks if the user is still oncall.
        user_start = layer["rendered_schedule_entries"][0]["user"]["id"]
        user_end = layer["rendered_schedule_entries"][-1]["user"]["id"]
        if user_start != user_end:
            # TODO: send_oncall_shift_feedback_message
            pass


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
