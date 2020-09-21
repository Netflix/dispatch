"""
.. module: dispatch.plugins.dispatch_metaflow.plugin
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from dispatch.plugins.bases import ExternalWorkflowPlugin
from dispatch.plugins import dispatch_metaflow as metaflow_plugin
from metaflow import Meson, MesonDuplicateSignal  # Metaflow, namespace, current

# from .config import METAFLOW_NAMESPACE

log = logging.getLogger(__name__)


class MetaflowExternalWorkflowPlugin(ExternalWorkflowPlugin):
    title = "Metaflow - External Workflows"
    slug = "metaflow-external-workflow"
    description = "Metaflow external workflow runner."
    version = metaflow_plugin.__version__

    author = "Netflix"
    author_url = "https://github.com/netflix/dispatch.git"

    def list(self, **kwargs):
        # this is currently too slow to be useable, we hard code for now, it's on the Metaflow roadmap.
        # namespace(METAFLOW_NAMESPACE)
        # flows = []
        # for flow in list(Metaflow()):
        #    flows.append({"id": flow.id, "params": flow.latest_run["start"].task.data.keys()})

        return [
            {
                "id": "sirtresponse.user.kglisson.ApplicationMetadataFlow",
                "name": "sirtresponse.user.kglisson.ApplicationMetadataFlow",
                "params": [{"name": "app", "type": "string"}],
            }
        ]

    def get(self, workflow_id: str, **kwargs):
        for w in self.list():
            if w["id"] == workflow_id:
                return w

    def run(self, workflow_id: str, params: dict, **kwargs):
        try:
            Meson.send_signal(workflow_id, params)
        except MesonDuplicateSignal:
            log.debug(
                f"Triggering signal already exists. WorkflowId: {workflow_id} Params: {params} Kwargs: {kwargs}"
            )
