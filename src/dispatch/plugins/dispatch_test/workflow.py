from dispatch.plugins.bases import WorkflowPlugin


class TestWorkflowPlugin(WorkflowPlugin):
    title = "Dispatch Test Plugin - Workflow"
    slug = "test-workflow"

    def get_instance(self, workflow_id: str, instance_id: str, **kwargs):
        return

    def run(self, workflow_id: str, params: dict, **kwargs):
        return
