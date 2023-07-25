from datetime import datetime, timedelta


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


def get_oncall_schedule(client, schedule_id: str, param={}) -> list[dict]:
    """Gets the oncall schedule."""
    if not param:
        # Grabs the oncall schedule from the last 24 hour by default
        param["until"] = datetime.now()
        param["since"] = param["until"] - timedelta(days=1)

    return client.rget(f"/schedules/{schedule_id}", param=param)


def send_feedback_form(user):
    """TODO(averyl): send the feedback form. There are more than one people on call during this time period."""
    pass


# @background_task
# TODO: Set default trigger time.
def oncall_shift_feedback_flow(client, schedule_id: str):
    schedule = get_oncall_schedule(client, schedule_id)
    schedule_layers = schedule["schedule"]["schedule_layers"]

    # Adds the override layer
    if schedule["overrides_subschedule"]:
        schedule_layers += schedule["overrides_subschedule"]

    for layer in schedule_layers:
        unique_users = list(set([entry.user.id for entry in layer["rendered_schedule_entries"]]))
        # Sends the feedback form to all users who have completed their oncall shifts.
        for user in unique_users[:-1]:
            send_feedback_form(user)


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
