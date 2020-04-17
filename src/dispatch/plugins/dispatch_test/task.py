from dispatch.plugins.bases import TaskPlugin


class TestTaskPlugin(TaskPlugin):
    title = "Dispatch Test Plugin - Task"
    slug = "test-task"

    def get(self, **kwargs):
        return

    def create(self, **kwargs):
        return

    def delete(self, **kwargs):
        return

    def list(self, **kwargs):
        return

    def resolve(self, **kwargs):
        return
