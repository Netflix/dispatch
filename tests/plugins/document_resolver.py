from dispatch.plugins.bases import DocumentResolverPlugin


class TestDocumentResolverPlugin(DocumentResolverPlugin):
    title = "Test Document Resovler"
    slug = "test-document-resolver"

    def get(self, items, **kwargs):
        return
