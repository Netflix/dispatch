from dispatch.plugins.bases import ParticipantGroupPlugin


class TestParticipantGroupPlugin(ParticipantGroupPlugin):
    title = "Test Participant Group"
    slug = "test-participant-group"

    def create(self, participants, **kwargs):
        return

    def add(self, participant, **kwargs):
        return

    def remove(self, participant, **kwargs):
        return
