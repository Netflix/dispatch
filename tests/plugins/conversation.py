from dispatch.plugins.bases import ConversationPlugin


class TestConversationPlugin(ConversationPlugin):
    title = "Test Conversation"
    slug = "test-conversation"

    def create(self, items, **kwargs):
        return

    def add(self, items, **kwargs):
        return

    def send(self, items, **kwargs):
        return
