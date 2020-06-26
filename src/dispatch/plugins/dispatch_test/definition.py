from dispatch.plugins.bases import DefinitionPlugin


class TestDefinitionPlugin(DefinitionPlugin):
    title = "Dispatch Test Plugin - Definition"
    slug = "test-definition"

    def get(self, key, **kwargs):
        return

    def create(self, key, **kwargs):
        return

    def update(self, key, **kwargs):
        return

    def delete(self, key, **kwargs):
        return

    def move(self, key, **kwargs):
        return
