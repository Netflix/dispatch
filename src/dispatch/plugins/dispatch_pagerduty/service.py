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

    # Grabs the oncall schedule from the last 24 hour by default
    if not param:
        param["until"] = datetime.now()
        param["since"] = param["until"] - timedelta(days=1)

    param["include[]"] = "schedule_layers"
    return client.rget(f"/schedules/{schedule_id}", param=param)


def send_shift_feedback_form_message(client, service_id: str):
    service = client.rget(f"/services/{service_id}")
    schedule = get_oncall_schedule(client, service)

    # TODO: How do we identify if an override has ended their shift? This could potentially go on indefinitely.
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

        # Sends the feedback form to all users who have completed their oncall shifts.
        unique_users = list(set([entry.user.id for entry in layer["rendered_schedule_entries"]]))
        for user in unique_users[:-1]:
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
