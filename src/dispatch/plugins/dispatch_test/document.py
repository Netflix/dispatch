from dispatch.plugins.bases import DocumentPlugin


class TestDocumentPlugin(DocumentPlugin):
    title = "Dispatch Test Plugin - Document"
    slug = "test-document"

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
