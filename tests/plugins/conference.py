from dispatch.plugins.bases import ConferencePlugin


class TestConferencePlugin(ConferencePlugin):
    title = "TestConference"
    slug = "test-conference"

    def create(self, items, **kwargs):
        return
