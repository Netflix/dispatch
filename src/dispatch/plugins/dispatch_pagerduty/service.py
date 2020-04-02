import pypd
from pypd.models.service import Service

from dispatch.exceptions import DispatchPluginException

from .config import PAGERDUTY_API_KEY, PAGERDUTY_API_FROM_EMAIL


pypd.api_key = PAGERDUTY_API_KEY


def get_oncall_email(service: Service):
    """Fetches the oncall's email for a given service."""
    escalation_policy_id = service.json["escalation_policy"]["id"]
    escalation_policy = pypd.EscalationPolicy.fetch(escalation_policy_id)

    schedule_id = escalation_policy.json["escalation_rules"][0]["targets"][0]["id"]

    oncall = pypd.OnCall.find_one(
        escalation_policy_ids=[escalation_policy_id], schedule_ids=[schedule_id]
    )

    user_id = oncall.json["user"]["id"]
    user = pypd.User.fetch(user_id)

    return user.json["email"]


def get_oncall(service_id: str = None, service_name: str = None):
    """Gets the oncall for a given service id or name."""
    if service_id:
        service = pypd.Service.fetch(service_id)
        return get_oncall_email(service)
    elif service_name:
        service = pypd.Service.find(query=service_name)

        if len(service) > 1:
            raise DispatchPluginException(
                f"More than one PagerDuty service found with service name: {service_name}"
            )

        if not service:
            raise DispatchPluginException(
                f"No on-call service found with service name: {service_name}"
            )

        return get_oncall_email(service[0])

    raise DispatchPluginException(f"Cannot fetch oncall. Must specify service_id or service_name.")


def page_oncall(
    service_id: str, incident_name: str, incident_title: str, incident_description: str
):
    """Pages the oncall for a given service id."""
    service = pypd.Service.fetch(service_id)
    escalation_policy_id = service.json["escalation_policy"]["id"]

    data = {
        "type": "incident",
        "title": f"{incident_name} - {incident_title}",
        "service": {"id": service_id, "type": "service_reference"},
        "incident_key": incident_name,
        "body": {"type": "incident_body", "details": incident_description},
        "escalation_policy": {"id": escalation_policy_id, "type": "escalation_policy_reference"},
    }

    incident = pypd.Incident.create(data=data, add_headers={"from": PAGERDUTY_API_FROM_EMAIL})

    return incident
