"""
.. module: dispatch.plugins.dispatch_pagerduty.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from pdpyras import APISession
from pydantic import Field, SecretStr, EmailStr
from typing import Optional
import logging

from dispatch.config import BaseConfigurationModel
from dispatch.decorators import apply, counter, timer
from dispatch.plugins import dispatch_pagerduty as pagerduty_oncall_plugin
from dispatch.plugins.bases import OncallPlugin

from .service import (
    get_oncall_email,
    page_oncall,
    oncall_shift_check,
    get_escalation_policy,
    get_service,
    get_next_oncall,
)


log = logging.getLogger(__name__)


class PagerdutyConfiguration(BaseConfigurationModel):
    """The values below are the available configurations for Dispatch's PagerDuty plugin."""

    api_key: SecretStr = Field(
        title="API Key",
        description="This is the key used to talk to the PagerDuty API. See: https://support.pagerduty.com/docs/generating-api-keys",
    )
    from_email: EmailStr = Field(
        title="From Email",
        description="This the email to put into the 'From' field of any page requests.",
    )
    pagerduty_api_url: str = Field(
        "https://api.pagerduty.com",
        title="Instance API URL",
        description="Enter the URL for your API (defaults to US)",
    )


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class PagerDutyOncallPlugin(OncallPlugin):
    title = "PagerDuty Plugin - Oncall Management"
    slug = "pagerduty-oncall"
    author = "Netflix"
    author_url = "https://github.com/Netflix/dispatch.git"
    description = "Uses PagerDuty to resolve and page oncall teams."
    version = pagerduty_oncall_plugin.__version__

    def __init__(self):
        self.configuration_schema = PagerdutyConfiguration

    def get(self, service_id: str) -> str:
        """Gets the current oncall person's email."""
        client = APISession(self.configuration.api_key.get_secret_value())
        client.url = self.configuration.pagerduty_api_url
        return get_oncall_email(client=client, service_id=service_id)

    def page(
        self,
        service_id: str,
        incident_name: str,
        incident_title: str,
        incident_description: str,
        **kwargs,
    ) -> dict:
        """Pages the oncall person."""
        client = APISession(self.configuration.api_key.get_secret_value())
        client.url = self.configuration.pagerduty_api_url
        return page_oncall(
            client=client,
            from_email=self.configuration.from_email,
            service_id=service_id,
            incident_name=incident_name,
            incident_title=incident_title,
            incident_description=incident_description,
        )

    def did_oncall_just_go_off_shift(self, schedule_id: str, hour: int) -> Optional[dict]:
        client = APISession(self.configuration.api_key.get_secret_value())
        client.url = self.configuration.pagerduty_api_url
        return oncall_shift_check(
            client=client,
            schedule_id=schedule_id,
            hour=hour,
        )

    def get_schedule_id_from_service_id(self, service_id: str) -> Optional[str]:
        if not service_id:
            return None

        try:
            client = APISession(self.configuration.api_key.get_secret_value())
            client.url = self.configuration.pagerduty_api_url
            service = get_service(
                client=client,
                service_id=service_id,
            )
            if service:
                escalation_policy_id = service["escalation_policy"]["id"]
                escalation_policy = get_escalation_policy(
                    client=client,
                    escalation_policy_id=escalation_policy_id,
                )
                if escalation_policy:
                    return escalation_policy["escalation_rules"][0]["targets"][0]["id"]
        except Exception as e:
            log.error("Error trying to retrieve schedule_id from service_id")
            log.exception(e)

    def get_next_oncall(self, service_id: str) -> Optional[str]:
        schedule_id = self.get_schedule_id_from_service_id(service_id)

        client = APISession(self.configuration.api_key.get_secret_value())
        client.url = self.configuration.pagerduty_api_url
        return get_next_oncall(
            client=client,
            schedule_id=schedule_id,
        )
