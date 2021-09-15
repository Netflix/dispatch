"""
.. module: dispatch.plugins.bases.workflow
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
from dispatch.plugins.base import Plugin


class WorkflowPlugin(Plugin):
    type = "workflow"

    def get_instance(self, workflow_id: str, instance_id: str, **kwargs):
        raise NotImplementedError

    def run(self, workflow_id: str, params: dict, **kwargs):
        raise NotImplementedError
