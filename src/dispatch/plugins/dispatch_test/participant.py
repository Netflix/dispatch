from dispatch.plugins.bases import ParticipantPlugin


class TestParticipantPlugin(ParticipantPlugin):
    title = "Test Participant"
    slug = "test-participant"

    def get(self, items, **kwargs):
        return
