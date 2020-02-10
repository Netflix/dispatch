from dispatch.plugins.bases import TermPlugin


class TestTermPlugin(TermPlugin):
    title = "Test Term"
    slug = "test-term"

    def get(self, **kwargs):
        return
