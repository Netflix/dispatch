from dispatch.plugins.bases import ParticipantPlugin


class TestParticipantPlugin(ParticipantPlugin):
    title = "Dispatch Test Plugin - Participant"
    slug = "test-participant"

    def get(self, items, **kwargs):
        return
