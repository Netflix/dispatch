"""
.. module: dispatch.plugins.generic_workflow.plugin
    :platform: Unix
    :copyright: (c) 2021 by Jørgen Teunis.
    :license: MIT, see LICENSE for more details.
    :description:

        The rest API needs to respond with JSON according to the JSON schema mentioned here
        https://github.com/Netflix/dispatch/issues/1722#issuecomment-947863678

        For example:
        {
            "status": "Completed",  # String<Running, Completed, Failed>
            "artifacts": [{
                "evergreen": False,
                "evergreen_owner": None,
                "evergreen_reminder_interval": 90,
                "evergreen_last_reminder_at": None,
                "resource_type": None,
                "resource_id": None,
                "weblink": "https://www.example.com",
                "description": "Description",
                "name": "Logfile20211020",
                "created_at": "2021-10-20 20:50:00",
                "updated_at": "2021-10-20 20:50:00"
            }],
            "weblink": "https://www.twitter.com", #String<WorkflowURL>,
        }

"""

import logging
import requests
import json

from pydantic import Field, SecretStr, AnyHttpUrl
from tenacity import TryAgain, retry, stop_after_attempt, wait_exponential

from dispatch.config import BaseConfigurationModel
from dispatch.decorators import apply, counter, timer
from dispatch.plugins import generic_workflow as generic_workflow_plugin
from dispatch.plugins.bases import WorkflowPlugin


class GenericWorkflowConfiguration(BaseConfigurationModel):
    """
    Generic Workflow configuration

    You can enter an REST API endpoint here that gets called when a workflow needs to either run or return its status.
    Run results in a POST request with a JSON payload containing workflow_id and params.
    Getting the status of the workflow is called as a GET request with the following GET query string parameters:
     workflow_id, workflow_instance_id, incident_id and incident_name.
    """

    api_url: AnyHttpUrl = Field(
        title="API URL", description="This API endpoint to GET or POST workflow info from/to."
    )
    auth_header: SecretStr = Field(
        title="Authorization Header",
        description="For example: Bearer: JWT token, or basic: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==",
    )


@apply(counter, exclude=["__init__"])
@apply(timer, exclude=["__init__"])
class GenericWorkflowPlugin(WorkflowPlugin):
    title = "Generic Workflow Plugin - Workflow Management"
    slug = "generic-workflow"
    description = "A generic workflow plugin that calls an API endpoint to kick-off a workflow and retrieve the status of a workflow."
    version = generic_workflow_plugin.__version__

    author = "Jørgen Teunis"
    author_url = "https://github.com/jtorvald/"

    def __init__(self):
        WorkflowPlugin.__init__(self)
        self.configuration_schema = GenericWorkflowConfiguration

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def get_workflow_instance(
        self,
        workflow_id: str,
        tags: list[str],
        **kwargs,
    ):
        api_url = self.configuration.api_url
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.configuration.auth_header.get_secret_value(),
        }
        fields = {
            "workflow_id": workflow_id,
            "tags": tags,
        }
        resp = requests.get(api_url, params=fields, headers=headers)

        if resp.status_code in [429, 500, 502, 503, 504]:
            raise TryAgain

        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def run(self, workflow_id: str, params: dict, **kwargs):
        logging.info("Run on generic workflow %s, %s", params, kwargs)
        api_url = self.configuration.api_url
        obj = {"workflow_id": workflow_id, "params": params}
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.configuration.auth_header.get_secret_value(),
        }
        resp = requests.post(api_url, data=json.dumps(obj), headers=headers)

        if resp.status_code in [429, 500, 502, 503, 504]:
            raise TryAgain

        return resp.json()
