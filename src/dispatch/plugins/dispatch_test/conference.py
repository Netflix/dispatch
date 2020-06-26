from dispatch.plugins.bases import ConferencePlugin


class TestConferencePlugin(ConferencePlugin):
    title = "Dispatch Test Plugin - Conference"
    slug = "test-conference"

    def create(self, items, **kwargs):
        return
