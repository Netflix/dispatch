from dispatch.plugins.bases import ContactPlugin


class TestContactPlugin(ContactPlugin):
    title = "Test Contact"
    slug = "test-contact"

    def get(self, key, **kwargs):
        return

    def create(self, key, **kwargs):
        return

    def update(self, key, **kwargs):
        return

    def delete(self, key, **kwargs):
        return

    def move(self, key, **kwargs):
        return
