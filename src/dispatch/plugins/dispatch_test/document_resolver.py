from dispatch.plugins.bases import DocumentResolverPlugin


class TestDocumentResolverPlugin(DocumentResolverPlugin):
    title = "Dispatch Test Plugin - Document Resolver"
    slug = "test-document-resolver"

    def get(self, items, **kwargs):
        return
