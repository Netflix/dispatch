from dispatch.plugins.bases import OncallPlugin


class TestOncallPlugin(OncallPlugin):
    title = "Test Oncall"
    slug = "test-oncall"

    def get(self, **kwargs):
        return
