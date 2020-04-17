from dispatch.plugins.bases import TermPlugin


class TestTermPlugin(TermPlugin):
    title = "Dispatch Test Plugin - Term"
    slug = "test-term"

    def get(self, **kwargs):
        return
